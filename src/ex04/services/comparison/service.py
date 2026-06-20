"""Deferred comparison service facade for Phase 6."""

from __future__ import annotations

from pathlib import Path

from ex04.services.comparison.interface import ComparisonServiceInterface
from ex04.shared.types import ComparisonReport, GraphData


class ComparisonService(ComparisonServiceInterface):
    """Comparison facade reserved for the Phase 6 implementation."""

    def run_comparison(
        self,
        bug_report: str,
        source_files: list[Path],
        graph_data: GraphData | None = None,
        vault_path: Path | None = None,
    ) -> ComparisonReport:
        """Fail explicitly until Phase 6 comparison runners are implemented."""
        raise NotImplementedError("Comparison service is implemented in Phase 6.")
