"""Analysis service facade implementing the analysis contract."""

from __future__ import annotations

from ex04.services.analysis.bug_report import BugReporter
from ex04.services.analysis.interface import AnalysisServiceInterface
from ex04.services.analysis.reverse_engineer import ReverseEngineer
from ex04.shared.types import GraphData, InvestigationResult


class AnalysisService(AnalysisServiceInterface):
    """Coordinate reverse engineering and bug report generation."""

    def __init__(
        self,
        reverse_engineer: ReverseEngineer | None = None,
        reporter: type[BugReporter] = BugReporter,
    ) -> None:
        """Initialize with optional component overrides."""
        self._reverse_engineer = reverse_engineer or ReverseEngineer()
        self._reporter = reporter

    def reverse_engineer(self, graph_data: GraphData) -> str:
        """Generate architecture notes from graph data."""
        return self._reverse_engineer.reverse_engineer(graph_data)

    def report(self, investigation: InvestigationResult) -> str:
        """Generate a structured bug report from an investigation."""
        return self._reporter.generate(investigation)

    def identify_patterns(self, graph_data: GraphData) -> list[str]:
        """Identify design patterns from graph data."""
        return self._reverse_engineer.identify_patterns(graph_data)
