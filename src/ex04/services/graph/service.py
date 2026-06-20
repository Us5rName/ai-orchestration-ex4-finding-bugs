"""Graph service facade implementing the graph contract."""

from __future__ import annotations

from pathlib import Path

from ex04.services.graph.analyzer import GraphAnalyzer
from ex04.services.graph.interface import GraphServiceInterface
from ex04.services.graph.parser import GraphParser
from ex04.services.graph.runner import GraphRunner
from ex04.shared.types import GraphData


class GraphService(GraphServiceInterface):
    """Coordinate graph extraction, parsing, and analysis components."""

    def __init__(
        self,
        runner: GraphRunner | None = None,
        parser: GraphParser | None = None,
        analyzer: GraphAnalyzer | None = None,
    ) -> None:
        """Initialize the service with optional component overrides."""
        self._runner = runner or GraphRunner()
        self._parser = parser or GraphParser()
        self._analyzer = analyzer or GraphAnalyzer()

    def extract(self, target_path: str) -> Path:
        """Extract a graph from a target codebase and return graph.json."""
        return self._runner.execute(target_path)

    def parse(self, graph_path: Path) -> GraphData:
        """Parse graph.json into structured graph data."""
        return self._parser.parse(graph_path)

    def analyze(self, graph_data: GraphData) -> dict[str, list]:
        """Analyze graph structure for centrality and communities."""
        ref_node = graph_data.entities[0].name if graph_data.entities else ""
        return {
            "god_nodes": self._analyzer.find_god_nodes(graph_data),
            "centrality_ranking": self._analyzer.rank_by_centrality(graph_data, ref_node),
            "communities": self._analyzer.detect_communities(graph_data),
        }
