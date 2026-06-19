"""Graph Service Interface — contract for graph operations.

Defines the abstract base class that all graph service implementations
must follow. Enables parallel development — other modules depend only
on this interface, not on concrete implementations.

See ADR-005 for rationale.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from pathlib import Path

from ex04.shared.types import GraphData


class GraphServiceInterface(ABC):
    """Abstract interface for graph service operations.

    All graph-related operations (execution, parsing, analysis) must
    implement this interface. This enables dependency injection and
    mock-based testing.
    """

    @abstractmethod
    def extract(self, target_path: str) -> Path:
        """Extract code graph from target codebase.

        Args:
            target_path: Path to the target codebase directory.

        Returns:
            Path to the generated graph.json output file.
        """

    @abstractmethod
    def parse(self, graph_path: Path) -> GraphData:
        """Parse graph output into structured data.

        Args:
            graph_path: Path to the graph.json file.

        Returns:
            Structured GraphData with entities, relationships, communities.
        """

    @abstractmethod
    def analyze(self, graph_data: GraphData) -> dict[str, list]:
        """Analyze graph structure for insights.

        Args:
            graph_data: Parsed graph data to analyze.

        Returns:
            Dict with keys 'god_nodes', 'centrality_ranking', 'communities'.
        """
