"""Tests for SignedMetricsCalculator.

Traceability: [PRD-CE §Metrics], [TODO T6.07]
"""

from __future__ import annotations

import pytest

from ex04.services.comparison.signed_metrics import SignedMetricsCalculator
from ex04.shared.types import RunMetrics


def _metrics(tokens: int = 0, files: int = 0, iters: int = 1, dur: float = 1.0,
             correct: bool = True) -> RunMetrics:
    return RunMetrics(
        tokens_used=tokens, files_read=files, iterations=iters,
        time_seconds=dur, found_root_cause=correct,
    )


def test_positive_savings() -> None:
    """Graph-guided uses fewer tokens → positive savings percentage."""
    calc = SignedMetricsCalculator()
    result = calc.compute(_metrics(tokens=1000), _metrics(tokens=600))
    assert result.token_savings_pct is not None
    assert result.token_savings_pct > 0


def test_negative_savings_preserved() -> None:
    """Graph-guided uses MORE tokens → negative savings, not clamped."""
    calc = SignedMetricsCalculator()
    result = calc.compute(_metrics(tokens=600), _metrics(tokens=1000))
    assert result.token_savings_pct is not None
    assert result.token_savings_pct < 0


def test_zero_token_baseline_returns_none() -> None:
    """Zero naive tokens → savings percentage is None, not error."""
    calc = SignedMetricsCalculator()
    result = calc.compute(_metrics(tokens=0), _metrics(tokens=500))
    assert result.token_savings_pct is None


def test_token_delta_signed() -> None:
    """token_delta is guided - naive (negative when guided is smaller)."""
    calc = SignedMetricsCalculator()
    result = calc.compute(_metrics(tokens=1000), _metrics(tokens=700))
    assert result.token_delta == -300


def test_file_delta() -> None:
    """file_delta is guided - naive."""
    calc = SignedMetricsCalculator()
    result = calc.compute(_metrics(files=10), _metrics(files=3))
    assert result.file_delta == -7


def test_iteration_delta() -> None:
    """iteration_delta is preserved."""
    calc = SignedMetricsCalculator()
    result = calc.compute(_metrics(iters=5), _metrics(iters=2))
    assert result.iteration_delta == -3


def test_duration_delta() -> None:
    """duration_delta is preserved."""
    calc = SignedMetricsCalculator()
    result = calc.compute(_metrics(dur=10.0), _metrics(dur=4.0))
    assert result.duration_delta == pytest.approx(-6.0)


def test_correctness_flags() -> None:
    """Correctness flags are preserved from RunMetrics."""
    calc = SignedMetricsCalculator()
    result = calc.compute(_metrics(correct=True), _metrics(correct=False))
    assert result.naive_correct is True
    assert result.guided_correct is False


def test_limitations_when_no_tokens() -> None:
    """Limitations note when token telemetry is unavailable."""
    calc = SignedMetricsCalculator()
    result = calc.compute(_metrics(tokens=0), _metrics(tokens=0))
    assert len(result.limitations) > 0
