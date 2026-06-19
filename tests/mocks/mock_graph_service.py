"""Mock Graph Service — synthetic graph data for testing."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from ex04.services.graph.interface import GraphServiceInterface
from ex04.shared.types import Community, Entity, GraphData, Relationship


class MockGraphService(GraphServiceInterface):
    """Mock implementation of GraphServiceInterface with synthetic data.

    Returns deterministic synthetic graph data for testing without
    invoking the real Grphify CLI.
    """

    def extract(self, target_path: str) -> Path:
        """Return a fake graph.json path.

        Args:
            target_path: Ignored in mock.

        Returns:
            Fake path to graph.json.
        """
        return Path("/tmp/mock-graph.json")

    def parse(self, graph_path: Path) -> GraphData:
        """Return synthetic graph data.

        Args:
            graph_path: Ignored in mock.

        Returns:
            GraphData with 3 entities, 3 relationships, 1 community.
        """
        return GraphData(
            entities=[
                Entity(name="main", kind="file", file_path="main.py", line_range=(1, 50)),
                Entity(name="utils", kind="file", file_path="utils.py", line_range=(1, 30)),
                Entity(
                    name="process_data", kind="function", file_path="main.py", line_range=(10, 25)
                ),
            ],
            relationships=[
                Relationship(source="main", target="utils", type="imports"),
                Relationship(source="process_data", target="utils", type="calls"),
                Relationship(source="main", target="process_data", type="calls"),
            ],
            communities=[
                Community(name="main_module", entities=["main", "process_data"], size=2),
            ],
        )

    def analyze(self, graph_data: GraphData) -> dict[str, list[Any]]:
        """Return synthetic analysis results.

        Args:
            graph_data: Graph data to analyze (ignored in mock).

        Returns:
            Dict with god_nodes, centrality_ranking, communities.
        """
        return {
            "god_nodes": ["main"],
            "centrality_ranking": [("main", 0.8), ("utils", 0.5), ("process_data", 0.3)],
            "communities": ["main_module"],
        }
