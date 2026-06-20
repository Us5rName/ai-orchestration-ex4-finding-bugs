"""Naive bounded investigation using ordinary repository navigation only."""

from __future__ import annotations

import os
import re
import time
from collections.abc import Sequence
from pathlib import Path

from ex04.providers.interface import Message
from ex04.services.comparison._output_parser import JSON_SCHEMA, parse_json_response
from ex04.services.comparison.anchors import validate_evidence_anchors
from ex04.services.comparison.budget import (
    BudgetExceededError,
    BudgetLedger,
    estimate_context_tokens,
)
from ex04.services.comparison.trace import TraceRecorder
from ex04.shared.gatekeeper import GatekeeperInterface
from ex04.shared.types_request import ComparisonRequest
from ex04.shared.types_results import InvestigationResult

_parse_json_response = parse_json_response


def _extract_keywords(bug_report: str) -> set[str]:
    words = re.findall(r"\b[a-zA-Z_]\w{2,}\b", bug_report.lower())
    return {
        word
        for word in words
        if word not in {"the", "and", "for", "with", "that", "this"}
    }


def _legacy_request(bug_report: str, runner: NaiveRunner) -> ComparisonRequest:
    return ComparisonRequest(
        bug_report=bug_report,
        provider=runner.provider,
        run_id="legacy-naive",
        max_files=runner.max_files,
        max_bytes=runner.max_bytes,
        timeout_seconds=int(runner.timeout_seconds),
    )


def _snapshot_root(files: Sequence[Path], request: ComparisonRequest) -> Path:
    if request.target_snapshot_path:
        return Path(request.target_snapshot_path)
    if not files:
        return Path(".")
    return Path(os.path.commonpath([str(p.parent.resolve()) for p in files]))


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
        req = _legacy_request(request, self) if isinstance(request, str) else request
        req.validate()
        ledger = budget or BudgetLedger.from_request(req)
        recorder = trace or TraceRecorder(req.run_id or "naive")
        started = time.perf_counter()
        context, limitations = self._build_context(req, source_files, ledger, recorder)
        response = self._call_provider(req, context, ledger, recorder)
        status, parsed = parse_json_response(response.text)
        evidence, anchor_lims = (
            validate_evidence_anchors(parsed, _snapshot_root(source_files, req))
            if parsed
            else ([], [])
        )
        limitations.extend(anchor_lims)
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
            mode=req.mode or "naive",
            config_hash=req.controlled_config_hash(),
            target_commit=req.target_commit,
        )

    def _build_context(
        self,
        req: ComparisonRequest,
        files: Sequence[Path],
        ledger: BudgetLedger,
        trace: TraceRecorder,
    ) -> tuple[str, list[str]]:
        keywords = _extract_keywords(req.bug_report)
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
