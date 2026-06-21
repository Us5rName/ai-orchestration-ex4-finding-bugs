"""Naive bounded investigation using ordinary repository navigation only."""

from __future__ import annotations

import time
from collections.abc import Sequence
from pathlib import Path

from ex04.services.comparison._output_parser import parse_json_response
from ex04.services.comparison.budget import (
    BudgetExceededError,
    BudgetLedger,
    estimate_context_tokens,
)
from ex04.services.comparison.call_service import ComparisonCallService
from ex04.services.comparison.context_bundle import (
    ContextBundle,
    ContextProvenance,
    ContextStrategy,
    SourceRef,
)
from ex04.services.comparison.naive_helpers import (
    anchored_evidence,
    build_naive_result,
    extract_keywords,
    legacy_request,
)
from ex04.services.comparison.prompt_builder import ComparisonPromptInput, PromptBuilder
from ex04.services.comparison.trace import TraceRecorder
from ex04.shared.gatekeeper import GatekeeperInterface
from ex04.shared.types_request import ComparisonRequest
from ex04.shared.types_results import InvestigationResult

_parse_json_response = parse_json_response
_prompt_builder = PromptBuilder()



class NaiveRunner:
    """Run ordinary search/read navigation without graph or vault context."""

    def __init__(
        self,
        gatekeeper: GatekeeperInterface,
        provider: str = "openai",
        max_files: int = 20,
        max_bytes: int = 524288,
        timeout_seconds: float = 120.0,
    ) -> None:
        self.gatekeeper = gatekeeper
        self.provider = provider
        self.max_files = max_files
        self.max_bytes = max_bytes
        self.timeout_seconds = timeout_seconds
        self._call_service = ComparisonCallService(gatekeeper)

    def run(
        self,
        request: ComparisonRequest | str,
        source_files: Sequence[Path],
        *,
        budget: BudgetLedger | None = None,
        trace: TraceRecorder | None = None,
    ) -> InvestigationResult:
        """Navigate source files, call provider once, and parse grounded output."""
        req = (
            legacy_request(
                request,
                provider=self.provider,
                max_files=self.max_files,
                max_bytes=self.max_bytes,
                timeout_seconds=self.timeout_seconds,
            )
            if isinstance(request, str)
            else request
        )
        req.validate()
        ledger = budget or BudgetLedger.from_request(req)
        recorder = trace or TraceRecorder(req.run_id or "naive")
        started = time.perf_counter()
        context, limitations = self._build_context(req, source_files, ledger, recorder)
        bundle = self._make_bundle(context, source_files)
        response = self._call_provider(req, bundle, ledger, recorder)
        status, parsed = parse_json_response(response.text)
        evidence, anchor_lims = anchored_evidence(parsed, source_files, req)
        limitations.extend(anchor_lims)
        diagnosis = "grounded_candidate" if status == "parsed_ok" and evidence else "unverified"
        return build_naive_result(req, ledger, response, status, parsed, evidence, limitations, started, diagnosis)

    def _build_context(
        self,
        req: ComparisonRequest,
        files: Sequence[Path],
        ledger: BudgetLedger,
        trace: TraceRecorder,
    ) -> tuple[str, list[str]]:
        keywords = extract_keywords(req.bug_report)
        parts: list[str] = []
        limitations: list[str] = []
        trace.record("tree_list", ledger, file_count=len(files))
        for path in sorted((p for p in files if p.is_file()), key=lambda p: p.name):
            if not keywords.intersection(path.name.lower().split("_")) and parts:
                continue
            try:
                text = path.read_text(encoding="utf-8", errors="replace")
                chunk = text[: max(0, req.max_bytes - ledger.bytes_read)]
                encoded_len = len(chunk.encode())
                tokens = estimate_context_tokens(chunk)
                ledger.check(files=1, bytes_=encoded_len, tokens=tokens, tools=1)
                ledger.record(files=1, bytes_=encoded_len, tokens=tokens, tools=1)
                trace.record("read_file", ledger, path=str(path), bytes=encoded_len)
                parts.append(f"--- {path.name} ---\n{chunk}")
            except (OSError, BudgetExceededError) as exc:
                limitations.append(str(exc))
                trace.budget_stop(ledger, str(exc))
                break
        return "\n\n".join(parts) if parts else "(no files read)", limitations

    def _make_bundle(self, context: str, files: Sequence[Path]) -> ContextBundle:
        """Wrap naive context text in a typed ContextBundle."""
        refs = tuple(SourceRef(path=str(f), kind="file") for f in files if f.is_file())
        prov = ContextProvenance(
            strategy=ContextStrategy.NAIVE,
            token_count=estimate_context_tokens(context),
            source_count=len(refs),
        )
        return ContextBundle(content=context, strategy=ContextStrategy.NAIVE,
                             source_refs=refs, provenance=prov)

    def _call_provider(
        self, req: ComparisonRequest, bundle: ContextBundle,
        ledger: BudgetLedger, trace: TraceRecorder,
    ):
        """Build canonical prompt and execute via shared call service."""
        inp = ComparisonPromptInput(system_prompt=req.system_prompt,
                                    bug_report=req.bug_report, context_bundle=bundle)
        return self._call_service.execute(
            _prompt_builder.build_messages(inp), req.provider, req.model, ledger, trace
        ).response
