"""Graph-guided bounded investigation workflow."""

from __future__ import annotations

import time
from pathlib import Path

from ex04.services.comparison._output_parser import parse_json_response
from ex04.services.comparison.anchors import validate_evidence_anchors
from ex04.services.comparison.budget import BudgetLedger, estimate_context_tokens
from ex04.services.comparison.call_service import ComparisonCallService
from ex04.services.comparison.context_bundle import (
    ContextBundle,
    ContextProvenance,
    ContextStrategy,
    SourceRef,
)
from ex04.services.comparison.graph_context_ops import graph_context, vault_context
from ex04.services.comparison.prompt_builder import ComparisonPromptInput, PromptBuilder
from ex04.services.comparison.trace import TraceRecorder
from ex04.shared.gatekeeper import GatekeeperInterface
from ex04.shared.types import GraphData
from ex04.shared.types_evidence import StructuredEvidence
from ex04.shared.types_request import ComparisonRequest
from ex04.shared.types_results import InvestigationResult

_prompt_builder = PromptBuilder()


def _legacy_request(bug_report: str, provider: str) -> ComparisonRequest:
    return ComparisonRequest(bug_report=bug_report, provider=provider, run_id="legacy-graph")


class GraphGuidedRunner:
    """Run the focused graph/vault-guided comparison mode."""

    def __init__(self, gatekeeper: GatekeeperInterface, provider: str = "openai") -> None:
        self.gatekeeper = gatekeeper
        self.provider = provider
        self._call_service = ComparisonCallService(gatekeeper)

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
            graph_data,
            req.bug_report,
            ledger,
            recorder,
        )
        vault_text, vault_ev, vault_lims = vault_context(vault_path, ledger, recorder)
        evidence.extend(vault_ev)
        limitations.extend(vault_lims)
        bundle = self._make_bundle(graph_text, vault_text, graph_data)
        response = self._call_provider(req, bundle, ledger, recorder)
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

    def _make_bundle(self, graph_text: str, vault_text: str, graph_data: GraphData | None) -> ContextBundle:
        """Wrap graph/vault context in a typed ContextBundle."""
        combined = f"{graph_text}\n\n{vault_text}" if vault_text else graph_text
        refs: tuple[SourceRef, ...] = ()
        if graph_data:
            refs = tuple(SourceRef(path=e.file_path or e.name, kind="node", label=e.name)
                         for e in graph_data.entities)
        prov = ContextProvenance(strategy=ContextStrategy.GRAPH_GUIDED,
                                 token_count=estimate_context_tokens(combined), source_count=len(refs))
        return ContextBundle(content=combined, strategy=ContextStrategy.GRAPH_GUIDED,
                             source_refs=refs, provenance=prov)

    def _call_provider(self, req: ComparisonRequest, bundle: ContextBundle,
                       ledger: BudgetLedger, trace: TraceRecorder):
        """Build canonical prompt and execute via shared call service."""
        inp = ComparisonPromptInput(system_prompt=req.system_prompt,
                                    bug_report=req.bug_report, context_bundle=bundle)
        return self._call_service.execute(
            _prompt_builder.build_messages(inp), req.provider, req.model, ledger, trace
        ).response

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
