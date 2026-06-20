"""Mock Analysis Service — canned analysis outputs for testing."""

from __future__ import annotations

from ex04.services.analysis.interface import AnalysisServiceInterface
from ex04.shared.types import GraphData, InvestigationResult


class MockAnalysisService(AnalysisServiceInterface):
    """Mock implementation of AnalysisServiceInterface with canned outputs.

    Returns deterministic reverse engineering summaries and bug reports
    for testing without invoking LLM APIs.
    """

    def reverse_engineer(self, graph_data: GraphData) -> str:
        """Return a canned architectural summary.

        Args:
            graph_data: Graph data (ignored in mock).

        Returns:
            Synthetic architectural summary string.
        """
        return (
            "# Architecture Summary\n\n"
            "## Block Diagram\n"
            "```mermaid\n"
            "graph TD\n"
            "    A[main.py] --> B[utils.py]\n"
            "    A --> C[process_data()]\n"
            "```\n\n"
            "## OOP Schema\n"
            "```mermaid\n"
            "classDiagram\n"
            "    class Main\n"
            "    class Utils\n"
            "    Main --> Utils\n"
            "```\n\n"
            "Detected 2 modules, 1 function, 2 relationships."
        )

    def report(self, investigation: InvestigationResult) -> str:
        """Return a canned bug report.

        Args:
            investigation: Investigation result (used for content).

        Returns:
            Formatted bug report string.
        """
        return (
            f"# Bug Report\n\n"
            f"**Root Cause**: {investigation.root_cause}\n\n"
            f"**Suspects**: {len(investigation.suspects)} location(s)\n\n"
            f"**Proposed Fix**: {investigation.proposed_fix}\n\n"
            f"**Fix Applied**: {investigation.fix_applied}"
        )

    def identify_patterns(self, graph_data: GraphData) -> list[str]:
        """Return a canned pattern list.

        Args:
            graph_data: Graph data (ignored in mock).

        Returns:
            Synthetic list of pattern description lines.
        """
        return ["- **Singleton** detected in 1 class."]
