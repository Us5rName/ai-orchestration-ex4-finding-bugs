"""Metrics Calculator — computes comparison metrics."""

from __future__ import annotations

from ex04.shared.types import ComparisonMetrics, RunMetrics


class MetricsCalculator:
    """Calculate savings between naive and graph-guided runs."""

    def compare(self, naive: RunMetrics, guided: RunMetrics) -> ComparisonMetrics:
        """Return side-by-side metrics with percentage savings."""
        return ComparisonMetrics(
            naive=naive,
            guided=guided,
            token_savings_pct=self._savings(naive.tokens_used, guided.tokens_used),
            file_read_savings_pct=self._savings(naive.files_read, guided.files_read),
            iteration_savings_pct=self._savings(naive.iterations, guided.iterations),
        )

    @staticmethod
    def _savings(naive_value: float, guided_value: float) -> float:
        """Calculate signed savings percentage (negative = regression).

        Returns 0.0 when the naive baseline is zero or negative.
        Negative values are preserved — regressions are valid evidence.
        """
        if naive_value <= 0:
            return 0.0
        return ((naive_value - guided_value) / naive_value) * 100
