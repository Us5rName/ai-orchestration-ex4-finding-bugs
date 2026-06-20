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

from ex04.providers.interface import Message
from ex04.services.comparison._output_parser import JSON_SCHEMA, parse_json_response
from ex04.services.comparison.anchors import validate_evidence_anchors
from ex04.services.comparison.budget import BudgetLedger
from ex04.services.comparison.graph_context_ops import graph_context, vault_context
from ex04.services.comparison.trace import TraceRecorder
from ex04.shared.gatekeeper import GatekeeperInterface
from ex04.shared.types import GraphData
from ex04.shared.types_evidence import StructuredEvidence
from ex04.shared.types_request import ComparisonRequest
from ex04.shared.types_results import InvestigationResult


def _legacy_request(bug_report: str, provider: str) -> ComparisonRequest:
    return ComparisonRequest(bug_report=bug_report, provider=provider, run_id="legacy-graph")


class GraphGuidedRunner:
    """Run a focused graph/vault-guided comparison pass."""

    def __init__(self, gatekeeper: GatekeeperInterface, provider: str = "openai") -> None:
        self.gatekeeper = gatekeeper
        self.provider = provider

    def run(
        self,
        request: ComparisonRequest | str,
        graph_data: GraphData | None = None,
        vault_path: Path | None = None,
        *,
        budget: BudgetLedger | None = None,
        trace: TraceRecorder | None = None,
    ) -> InvestigationResult:
        """Acquire graph/vault context, call provider, and validate anchors."""
        req = _legacy_request(request, self.provider) if isinstance(request, str) else request
        req.validate()
        ledger = budget or BudgetLedger.from_request(req)
        recorder = trace or TraceRecorder(req.run_id or "graph")
        started = time.perf_counter()
        graph_text, evidence, limitations = graph_context(
            graph_data, req.bug_report, ledger, recorder
        )
        vault_text, vault_ev, vault_lims = vault_context(vault_path, ledger, recorder)
        evidence.extend(vault_ev)
        limitations.extend(vault_lims)
        response = self._call_provider(req, graph_text, vault_text, ledger, recorder)
        status, parsed = parse_json_response(response.text)
        if parsed and req.target_snapshot_path:
            anchors, anchor_lims = validate_evidence_anchors(
                parsed,
                Path(req.target_snapshot_path),
            )
            evidence.extend(anchors)
            limitations.extend(anchor_lims)
        self._mark_referenced(parsed, evidence)
        diagnosis = "grounded_candidate" if status == "parsed_ok" and evidence else "unverified"
        return InvestigationResult(
            root_cause=str(parsed.get("root_cause", "")) if parsed else "",
            proposed_fix=str(parsed.get("patch", "")) if parsed else "",
            original_problem=req.bug_report,
            files_read=ledger.files_read,
            bytes_read=ledger.bytes_read,
            context_tokens=ledger.context_tokens,
            tool_calls=ledger.tool_calls,
            model_calls=ledger.model_calls,
            iterations=ledger.iterations,
            retries=ledger.retries,
            duration_seconds=time.perf_counter() - started,
            input_tokens=response.input_tokens,
            output_tokens=response.output_tokens,
            parser_status=status,
            diagnosis_status=diagnosis,
            gate_status="not_requested" if not req.gate_enabled else "not_run",
            verification_status="unverified",
            evidence=evidence,
            limitations=limitations + ledger.limitations,
            evidence_class=req.evidence_class,
            telemetry_available=response.input_tokens > 0 or response.output_tokens > 0,
            run_id=req.run_id,
            mode=req.mode or "graph",
            config_hash=req.controlled_config_hash(),
            target_commit=req.target_commit,
        )

    def _call_provider(
        self,
        req: ComparisonRequest,
        graph_text: str,
        vault_text: str,
        ledger: BudgetLedger,
        trace: TraceRecorder,
    ):
        ledger.check(models=1, iterations=1)
        content = (
            f"{req.system_prompt}\nBug:\n{req.bug_report}\n\n"
            f"{graph_text}\n\n{vault_text}\n\n{JSON_SCHEMA}"
        )
        messages: list[Message] = [{"role": "user", "content": content}]
        response = self.gatekeeper.send(req.provider, messages)
        ledger.record(models=1, iterations=1)
        trace.record("provider_call", ledger, provider=req.provider, model=req.model)
        return response

    @staticmethod
    def _mark_referenced(
        parsed: dict[str, object] | None,
        evidence: list[StructuredEvidence],
    ) -> None:
        if not parsed:
            return
        diagnosed = set(_string_items(parsed.get("suspected_files", [])))
        diagnosed |= set(_string_items(parsed.get("suspected_symbols", [])))
        for ev in evidence:
            if ev.source_file in diagnosed or ev.symbol in diagnosed:
                ev.in_final_diagnosis = True


def _string_items(value: object) -> list[str]:
    if not isinstance(value, list):
        return []
    return [item for item in value if isinstance(item, str)]
