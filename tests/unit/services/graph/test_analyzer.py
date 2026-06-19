"""Tests for GraphAnalyzer implementation (T4.03).

Tests GraphAnalyzer against GraphServiceInterface contract:
- find_god_nodes(graph) identifies high-degree nodes
- rank_by_centrality(graph, ref_node) ranks by proximity
- detect_communities(graph) extracts community clusters
"""

from __future__ import annotations

import pytest

from ex04.services.graph.analyzer import GraphAnalyzer
from ex04.shared.types import Community, Entity, GraphData, Relationship


class TestGraphAnalyzerFindGodNodes:
    """Tests for GraphAnalyzer.find_god_nodes() method."""

    def test_find_god_nodes_identifies_high_degree(self) -> None:
        """Test that find_god_nodes() identifies high-degree nodes."""
        graph = GraphData(
            entities=[
                Entity(name="a", kind="class"),
                Entity(name="b", kind="class"),
                Entity(name="c", kind="class"),
            ],
            relationships=[
                Relationship(source="a", target="b", type="calls"),
                Relationship(source="a", target="c", type="calls"),
                Relationship(source="b", target="c", type="calls"),
            ],
        )
        analyzer = GraphAnalyzer()
        god_nodes = analyzer.find_god_nodes(graph)
        assert len(god_nodes) >= 1
        assert "a" in god_nodes or "b" in god_nodes or "c" in god_nodes

    def test_find_god_nodes_empty_graph(self) -> None:
        """Test that find_god_nodes() returns empty list for empty graph."""
        graph = GraphData()
        analyzer = GraphAnalyzer()
        god_nodes = analyzer.find_god_nodes(graph)
        assert god_nodes == []


class TestGraphAnalyzerRankByCentrality:
    """Tests for GraphAnalyzer.rank_by_centrality() method."""

    def test_rank_by_centrality_returns_list(self) -> None:
        """Test that rank_by_centrality() returns a list of tuples."""
        graph = GraphData(
            entities=[Entity(name="a", kind="class"), Entity(name="b", kind="class")],
            relationships=[Relationship(source="a", target="b", type="calls")],
        )
        analyzer = GraphAnalyzer()
        ranking = analyzer.rank_by_centrality(graph, "a")
        assert isinstance(ranking, list)
        assert len(ranking) >= 1

    def test_rank_by_centrality_ref_node_first(self) -> None:
        """Test that ref_node appears first in ranking."""
        graph = GraphData(
            entities=[Entity(name="a", kind="class"), Entity(name="b", kind="class")],
            relationships=[Relationship(source="a", target="b", type="calls")],
        )
        analyzer = GraphAnalyzer()
        ranking = analyzer.rank_by_centrality(graph, "a")
        assert ranking[0] == ("a", pytest.approx(1.0, abs=0.1))


class TestGraphAnalyzerDetectCommunities:
    """Tests for GraphAnalyzer.detect_communities() method."""

    def test_detect_communities_returns_list(self) -> None:
        """Test that detect_communities() returns a list of communities."""
        graph = GraphData(
            entities=[Entity(name="a", kind="class"), Entity(name="b", kind="class")],
            relationships=[Relationship(source="a", target="b", type="calls")],
            communities=[Community(name="group1", entities=["a", "b"], size=2)],
        )
        analyzer = GraphAnalyzer()
        communities = analyzer.detect_communities(graph)
        assert isinstance(communities, list)

    def test_detect_communities_empty_graph(self) -> None:
        """Test that detect_communities() returns empty list for empty graph."""
        graph = GraphData()
        analyzer = GraphAnalyzer()
        communities = analyzer.detect_communities(graph)
        assert communities == []
