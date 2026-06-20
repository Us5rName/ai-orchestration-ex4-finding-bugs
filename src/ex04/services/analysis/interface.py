"""Analysis Service Interface — contract for analysis operations.

Defines the abstract base class that all analysis service implementations
must follow. Enables parallel development — other modules depend only
on this interface, not on concrete implementations.

See ADR-005 for rationale.

Implementation: Phase 4 (T4.16–T4.18)
  - T4.16: ReverseEngineer (reverse_engineer.py)
  - T4.17: DiagramGenerator (diagram_gen.py)
  - T4.18: BugReporter (bug_report.py)
"""

from __future__ import annotations

from abc import ABC, abstractmethod

from ex04.shared.types import GraphData, InvestigationResult


class AnalysisServiceInterface(ABC):
    """Abstract interface for analysis service operations.

    All analysis-related operations (reverse engineering, reporting) must
    implement this interface. This enables dependency injection and
    mock-based testing.
    """

    @abstractmethod
    def reverse_engineer(self, graph_data: GraphData) -> str:
        """Reverse engineer architecture from graph data.

        Args:
            graph_data: Parsed graph data to analyze.

        Returns:
            Human-readable architectural summary (Mermaid diagrams + text).
        """

    @abstractmethod
    def report(self, investigation: InvestigationResult) -> str:
        """Generate a structured bug report.

        Args:
            investigation: Investigation result to report on.

        Returns:
            Formatted bug report string.
        """

    @abstractmethod
    def identify_patterns(self, graph_data: GraphData) -> list[str]:
        """Identify common design patterns in graph data.

        Args:
            graph_data: Parsed graph data to analyze.

        Returns:
            List of markdown-formatted pattern description lines.
        """
