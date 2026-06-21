"""Helper functions for the naive comparison runner."""

from __future__ import annotations

import os
import re
from collections.abc import Sequence
from pathlib import Path

from ex04.services.comparison.anchors import validate_evidence_anchors
from ex04.shared.types_request import ComparisonRequest

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


def _snapshot_root(files: Sequence[Path], request: ComparisonRequest) -> Path:
    if request.target_snapshot_path:
        return Path(request.target_snapshot_path)
    if not files:
        return Path(".")
    return Path(os.path.commonpath([str(path.parent.resolve()) for path in files]))
