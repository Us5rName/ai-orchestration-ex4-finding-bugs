"""Comparison Service Interface — contract for comparison operations.

Defines the abstract base class that all comparison service implementations
must follow. Enables parallel development — other modules depend only
on this interface, not on concrete implementations.

See ADR-005 for rationale.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from pathlib import Path

from ex04.shared.types import ComparisonReport, GraphData


class ComparisonServiceInterface(ABC):
    """Abstract interface for comparison service operations.

    All comparison-related operations (running both approaches, comparing)
    must implement this interface. This enables dependency injection and
    mock-based testing.
    """

    @abstractmethod
    def run_comparison(
        self,
        bug_report: str,
        source_files: list[Path],
        graph_data: GraphData | None = None,
        vault_path: Path | None = None,
    ) -> ComparisonReport:
        """Run naive and guided approaches and compare metrics.

        Args:
            bug_report: Description of the bug to investigate.
            source_files: List of source file paths for naive approach.
            graph_data: Optional graph data for guided approach.
            vault_path: Optional vault path for guided approach.

        Returns:
            ComparisonReport with side-by-side metrics and narrative.
        """
