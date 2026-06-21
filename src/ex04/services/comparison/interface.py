"""Comparison Service Interface — contract for comparison operations.

Defines the abstract base class that all comparison service implementations
must follow. Enables parallel development — other modules depend only
on this interface, not on concrete implementations.

See ADR-005 for rationale.

Implementation: Phase 6 (T6.01–T6.03)
  - T6.01: NaiveRunner (naive_runner.py)
  - T6.02: GraphGuidedRunner (graph_guided_runner.py)
  - T6.03: MetricsCalculator (metrics.py)
  - T6.04: ReportGenerator (report_gen.py)
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from collections.abc import Sequence
from pathlib import Path

from ex04.services.comparison.graph_diff.models import PostGraphStatus
from ex04.shared.types import ComparisonReport, GraphData
from ex04.shared.types_experiment import ComparisonOutcome
from ex04.shared.types_request import ComparisonRequest


class ComparisonServiceInterface(ABC):
    """Abstract interface for comparison service operations.

    All comparison-related operations (running both approaches, comparing)
    must implement this interface. This enables dependency injection and
    mock-based testing.
    """

    @abstractmethod
    def run_comparison(
        self,
        request: ComparisonRequest | str,
        source_files: Sequence[Path],
        graph_data: GraphData | None = None,
        vault_path: Path | None = None,
        *,
        post_graph: GraphData | None = None,
        post_graph_status: PostGraphStatus | None = None,
        post_graph_error: str = "",
    ) -> ComparisonOutcome | ComparisonReport:
        """Run naive and guided approaches and compare metrics.

        Args:
            request: Canonical comparison request or legacy bug-report string.
            source_files: List of source file paths for naive approach.
            graph_data: Optional graph data for guided approach.
            vault_path: Optional vault path for guided approach.

        Returns:
            ComparisonReport with side-by-side metrics and narrative.
        """
