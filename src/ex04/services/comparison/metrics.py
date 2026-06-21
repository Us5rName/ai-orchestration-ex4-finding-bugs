"""Metrics Calculator — computes comparison metrics."""

from __future__ import annotations

from ex04.services.comparison.metrics_utils import pct_savings
from ex04.shared.types import ComparisonMetrics, RunMetrics


class MetricsCalculator:
    """Calculate savings between naive and graph-guided runs."""

    def compare(self, naive: RunMetrics, guided: RunMetrics) -> ComparisonMetrics:
        """Return side-by-side metrics with percentage savings."""
        return ComparisonMetrics(
            naive=naive,
            guided=guided,
            token_savings_pct=pct_savings(naive.tokens_used, guided.tokens_used),
            file_read_savings_pct=pct_savings(naive.files_read, guided.files_read),
            iteration_savings_pct=pct_savings(naive.iterations, guided.iterations),
        )
