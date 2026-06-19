"""Mock Comparison Service — canned comparison metrics for testing."""

from __future__ import annotations

from pathlib import Path

from ex04.services.comparison.interface import ComparisonServiceInterface
from ex04.shared.types import ComparisonMetrics, ComparisonReport, GraphData, RunMetrics


class MockComparisonService(ComparisonServiceInterface):
    """Mock implementation of ComparisonServiceInterface with canned metrics.

    Returns deterministic comparison reports for testing without
    running real naive or guided investigation workflows.
    """

    def run_comparison(
        self,
        bug_report: str,
        source_files: list[Path],
        graph_data: GraphData | None = None,
        vault_path: Path | None = None,
    ) -> ComparisonReport:
        """Return a canned comparison report.

        Args:
            bug_report: Bug description (ignored in mock).
            source_files: Source file list (ignored in mock).
            graph_data: Optional graph data (ignored in mock).
            vault_path: Optional vault path (ignored in mock).

        Returns:
            ComparisonReport with synthetic metrics showing token savings.
        """
        naive = RunMetrics(
            tokens_used=5000,
            files_read=20,
            iterations=10,
            time_seconds=120.0,
            found_root_cause=True,
        )
        guided = RunMetrics(
            tokens_used=2000, files_read=5, iterations=4, time_seconds=45.0, found_root_cause=True
        )
        metrics = ComparisonMetrics(
            naive=naive,
            guided=guided,
            token_savings_pct=60.0,
            file_read_savings_pct=75.0,
            iteration_savings_pct=60.0,
        )
        return ComparisonReport(
            metrics=metrics,
            narrative=(
                "The graph-guided approach saved 60% of tokens "
                "and 75% of file reads compared to the naive baseline."
            ),
            token_savings=3000,
        )
