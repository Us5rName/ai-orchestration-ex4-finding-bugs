"""Adapters from investigation results to comparison metric inputs."""

from __future__ import annotations

from collections.abc import Callable

from ex04.shared.types import RunMetrics
from ex04.shared.types_results import InvestigationResult

_SUCCESS_GATE_STATUSES = frozenset({"passed", "pass_without_gate"})


def _verified(result: InvestigationResult) -> bool:
    return result.verification_status == "verified"


def _accepted_gate(result: InvestigationResult) -> bool:
    return result.gate_status in _SUCCESS_GATE_STATUSES


def _parsed(result: InvestigationResult) -> bool:
    return result.parser_status == "parsed_ok"


_SUCCESS_CHECKS: tuple[Callable[[InvestigationResult], bool], ...] = (
    _verified,
    _accepted_gate,
    _parsed,
)


def found_root_cause(result: InvestigationResult) -> bool:
    """Return whether a result should count as a successful diagnosis."""
    if result.parser_status == "parse_failed":
        return False
    return any(check(result) for check in _SUCCESS_CHECKS)


def result_to_run_metrics(result: InvestigationResult) -> RunMetrics:
    """Bridge InvestigationResult to RunMetrics for legacy calculators."""
    tokens = (result.input_tokens or 0) + (result.output_tokens or 0)
    return RunMetrics(
        tokens_used=tokens,
        files_read=result.files_read,
        iterations=result.iterations,
        time_seconds=result.duration_seconds,
        found_root_cause=found_root_cause(result),
    )
