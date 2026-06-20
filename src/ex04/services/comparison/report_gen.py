"""Report Generator — generates comparison reports."""

from __future__ import annotations

from ex04.shared.types import ComparisonMetrics, ComparisonReport


class ReportGenerator:
    """Generate human-readable comparison summaries."""

    def generate(self, metrics: ComparisonMetrics) -> ComparisonReport:
        """Return a report with Markdown narrative and token savings."""
        token_savings = metrics.naive.tokens_used - metrics.guided.tokens_used
        narrative = (
            "| Metric | Naive | Graph-guided | Savings |\n"
            "|---|---:|---:|---:|\n"
            f"| Tokens | {metrics.naive.tokens_used} | {metrics.guided.tokens_used} | "
            f"{metrics.token_savings_pct:.1f}% |\n"
            f"| Files read | {metrics.naive.files_read} | {metrics.guided.files_read} | "
            f"{metrics.file_read_savings_pct:.1f}% |\n"
            f"| Iterations | {metrics.naive.iterations} | {metrics.guided.iterations} | "
            f"{metrics.iteration_savings_pct:.1f}% |"
        )
        return ComparisonReport(metrics=metrics, narrative=narrative, token_savings=token_savings)
