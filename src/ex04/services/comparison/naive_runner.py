"""Naive bounded investigation using ordinary repository navigation only."""

from __future__ import annotations

import time
from collections.abc import Sequence
from pathlib import Path

from ex04.providers.interface import Message
from ex04.services.comparison._output_parser import JSON_SCHEMA, parse_json_response
from ex04.services.comparison.budget import (
    BudgetExceededError,
    BudgetLedger,
    estimate_context_tokens,
)
from ex04.services.comparison.naive_helpers import (
    anchored_evidence,
    extract_keywords,
    legacy_request,
    parsed_str,
)
from ex04.services.comparison.trace import TraceRecorder
from ex04.shared.gatekeeper import GatekeeperInterface
from ex04.shared.types_request import ComparisonRequest
from ex04.shared.types_results import InvestigationResult

_parse_json_response = parse_json_response


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
        response = self._call_provider(req, context, ledger, recorder)
        status, parsed = parse_json_response(response.text)
        evidence, anchor_lims = anchored_evidence(parsed, source_files, req)
        limitations.extend(anchor_lims)
        diagnosis = "grounded_candidate" if status == "parsed_ok" and evidence else "unverified"
        result = InvestigationResult(
            root_cause=parsed_str(parsed, "root_cause"),
            proposed_fix=parsed_str(parsed, "patch"),
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
            mode=req.mode or "naive",
            config_hash=req.controlled_config_hash(),
            target_commit=req.target_commit,
        )
        return result

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

    def _call_provider(
        self,
        req: ComparisonRequest,
        context: str,
        ledger: BudgetLedger,
        trace: TraceRecorder,
    ):
        ledger.check(models=1, iterations=1)
        content = f"{req.system_prompt}\nBug:\n{req.bug_report}\n\n{context}\n\n{JSON_SCHEMA}"
        messages: list[Message] = [{"role": "user", "content": content}]
        response = self.gatekeeper.send(req.provider, messages)
        ledger.record(models=1, iterations=1)
        trace.record("provider_call", ledger, provider=req.provider, model=req.model)
        return response
