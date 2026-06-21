"""Helper functions for the naive comparison runner."""

from __future__ import annotations

import os
import re
import time
from collections.abc import Sequence
from pathlib import Path

from ex04.services.comparison.anchors import validate_evidence_anchors
from ex04.shared.types_request import ComparisonRequest
from ex04.shared.types_results import InvestigationResult, ProviderResponse

_STOP_WORDS = frozenset({"the", "and", "for", "with", "that", "this"})


def extract_keywords(bug_report: str) -> set[str]:
    words = re.findall(r"\b[a-zA-Z_]\w{2,}\b", bug_report.lower())
    return {word for word in words if word not in _STOP_WORDS}


def legacy_request(
    bug_report: str,
    *,
    provider: str,
    max_files: int,
    max_bytes: int,
    timeout_seconds: float,
) -> ComparisonRequest:
    return ComparisonRequest(
        bug_report=bug_report,
        provider=provider,
        run_id="legacy-naive",
        max_files=max_files,
        max_bytes=max_bytes,
        timeout_seconds=int(timeout_seconds),
    )


def anchored_evidence(
    parsed: dict[str, object] | None,
    files: Sequence[Path],
    request: ComparisonRequest,
):
    return (
        validate_evidence_anchors(parsed, _snapshot_root(files, request))
        if parsed
        else ([], [])
    )


def parsed_str(parsed: dict[str, object] | None, key: str) -> str:
    return str(parsed.get(key, "")) if parsed else ""


def build_naive_result(
    req: ComparisonRequest, ledger: object, response: ProviderResponse,
    status: str, parsed: dict | None, evidence: list, limitations: list,
    started: float, diagnosis: str,
) -> InvestigationResult:
    """Build the canonical InvestigationResult from a completed naive run."""
    from ex04.services.comparison.budget import BudgetLedger
    lg: BudgetLedger = ledger  # type: ignore[assignment]
    return InvestigationResult(
        root_cause=parsed_str(parsed, "root_cause"),
        proposed_fix=parsed_str(parsed, "patch"),
        original_problem=req.bug_report,
        files_read=lg.files_read, bytes_read=lg.bytes_read,
        context_tokens=lg.context_tokens, tool_calls=lg.tool_calls,
        model_calls=lg.model_calls, iterations=lg.iterations,
        retries=lg.retries, duration_seconds=time.perf_counter() - started,
        input_tokens=response.input_tokens, output_tokens=response.output_tokens,
        parser_status=status, diagnosis_status=diagnosis,
        gate_status="not_requested" if not req.gate_enabled else "not_run",
        verification_status="unverified", evidence=evidence,
        limitations=limitations + lg.limitations, evidence_class=req.evidence_class,
        telemetry_available=response.input_tokens > 0 or response.output_tokens > 0,
        run_id=req.run_id, mode=req.mode or "naive",
        config_hash=req.controlled_config_hash(), target_commit=req.target_commit,
    )


def _snapshot_root(files: Sequence[Path], request: ComparisonRequest) -> Path:
    if request.target_snapshot_path:
        return Path(request.target_snapshot_path)
    if not files:
        return Path(".")
    return Path(os.path.commonpath([str(path.parent.resolve()) for path in files]))
