"""Graph Guided Runner — executes graph-guided investigation workflow.

Uses bug-report-sensitive ranked graph entities, relationships, source
anchors, and vault notes to provide focused context. The independent
variable vs. NaiveRunner. Every entity sent to the model is recorded
as a StructuredEvidence entry in the returned InvestigationResult.

Traceability: [PRD-GGI §Contracts], [TODO P6-R04], [P6-R04-ext]
"""

from __future__ import annotations

import time
from pathlib import Path

from ex04.services.comparison._context_builder import (
    build_graph_context,
    build_vault_context,
)
from ex04.services.comparison._output_parser import JSON_SCHEMA, parse_json_response
from ex04.shared.gatekeeper import GatekeeperInterface
from ex04.shared.types import GraphData
from ex04.shared.types_evidence import StructuredEvidence
from ex04.shared.types_results import InvestigationResult


class GraphGuidedRunner:
    """Run a focused graph/vault-guided comparison pass.

    Context is derived from graph_data and the vault — no filesystem scan.
    Entities are ranked by multiple signals. Every entity and vault note
    sent to the model is recorded in InvestigationResult.evidence.
    """

    def __init__(self, gatekeeper: GatekeeperInterface, provider: str = "openai") -> None:
        """Initialize with Gatekeeper dependency."""
        self.gatekeeper = gatekeeper
        self.provider = provider

    def run(
        self,
        bug_report: str,
        graph_data: GraphData | None = None,
        vault_path: Path | None = None,
    ) -> InvestigationResult:
        """Use graph entities and vault notes before asking the model.

        Args:
            bug_report: Natural-language bug description.
            graph_data: Parsed Graphify output with entities and relationships.
            vault_path: Root of Obsidian vault (optional).

        Returns:
            InvestigationResult with full evidence list and budget telemetry.
        """
        started = time.perf_counter()
        evidence: list[StructuredEvidence] = []
        limitations: list[str] = []

        graph_ctx, _anchors, graph_lims = build_graph_context(
            graph_data, bug_report, evidence
        )
        limitations.extend(graph_lims)

        vault_ctx, files_read, vault_lims = build_vault_context(vault_path, evidence)
        limitations.extend(vault_lims)

        response = self.gatekeeper.send(
            self.provider,
            [{"role": "user", "content": (
                f"Bug:\n{bug_report}\n\n{graph_ctx}\n\n{vault_ctx}\n\n{JSON_SCHEMA}"
            )}],
        )

        parser_status, parsed = parse_json_response(response.text)
        if parsed:
            diagnosed = set(parsed.get("suspected_files", []))
            for ev in evidence:
                if ev.source_file in diagnosed or ev.symbol in diagnosed:
                    ev.in_final_diagnosis = True

        return InvestigationResult(
            root_cause=str(parsed.get("root_cause", "")) if parsed else "",
            proposed_fix=str(parsed.get("patch", "")) if parsed else "",
            original_problem=bug_report,
            files_read=files_read,
            bytes_read=0,
            tool_calls=len(evidence) + 1,
            model_calls=1,
            iterations=1,
            duration_seconds=time.perf_counter() - started,
            input_tokens=response.input_tokens,
            output_tokens=response.output_tokens,
            parser_status=parser_status,
            gate_status="pass_without_gate",
            evidence=evidence,
            limitations=limitations,
            evidence_class="fixture",
            telemetry_available=False,
        )
