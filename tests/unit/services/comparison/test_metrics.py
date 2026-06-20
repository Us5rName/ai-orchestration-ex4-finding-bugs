"""Tests for comparison metrics calculation."""

from ex04.services.comparison.metrics import MetricsCalculator
from ex04.shared.types import RunMetrics


def test_compare_calculates_savings() -> None:
    """Savings percentages are computed from naive baseline."""
    metrics = MetricsCalculator().compare(
        RunMetrics(tokens_used=100, files_read=10, iterations=4),
        RunMetrics(tokens_used=40, files_read=2, iterations=2),
    )

    assert metrics.token_savings_pct == 60.0
    assert metrics.file_read_savings_pct == 80.0
    assert metrics.iteration_savings_pct == 50.0


def test_compare_handles_zero_baseline() -> None:
    """Zero naive baseline produces zero savings instead of division error."""
    metrics = MetricsCalculator().compare(RunMetrics(), RunMetrics(tokens_used=10))

    assert metrics.token_savings_pct == 0.0
