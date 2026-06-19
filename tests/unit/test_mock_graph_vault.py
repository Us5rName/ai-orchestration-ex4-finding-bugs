"""Tests for MockGraphService and MockVaultService."""

from __future__ import annotations

from pathlib import Path

from ex04.shared.types import (
    Community,
    Entity,
    GraphData,
    Relationship,
)
from tests.mocks.mock_graph_service import MockGraphService
from tests.mocks.mock_vault_service import MockVaultService


class TestMockGraphService:
    """Tests for MockGraphService."""

    def test_extract_returns_path(self) -> None:
        mock = MockGraphService()
        result = mock.extract("/fake/path")
        assert isinstance(result, Path)

    def test_parse_returns_graph_data(self) -> None:
        mock = MockGraphService()
        result = mock.parse(Path("/fake/graph.json"))
        assert isinstance(result, GraphData)
        assert len(result.entities) == 3
        assert len(result.relationships) == 3
        assert len(result.communities) == 1
        assert isinstance(result.entities[0], Entity)
        assert isinstance(result.relationships[0], Relationship)
        assert isinstance(result.communities[0], Community)

    def test_analyze_returns_dict(self) -> None:
        mock = MockGraphService()
        graph_data = mock.parse(Path("/fake/graph.json"))
        result = mock.analyze(graph_data)
        assert isinstance(result, dict)
        assert "god_nodes" in result
        assert "centrality_ranking" in result
        assert "communities" in result


class TestMockVaultService:
    """Tests for MockVaultService."""

    def test_build_returns_dict_of_paths(self) -> None:
        mock = MockVaultService()
        graph_data = GraphData()
        result = mock.build(graph_data)
        assert isinstance(result, dict)
        for value in result.values():
            assert isinstance(value, Path)

    def test_navigate_returns_list_of_dicts(self) -> None:
        mock = MockVaultService()
        result = mock.navigate("test query")
        assert isinstance(result, list)
        assert len(result) > 0
        assert "title" in result[0]
        assert "path" in result[0]
        assert "content" in result[0]

    def test_update_returns_path(self) -> None:
        mock = MockVaultService()
        result = mock.update("hot", "Test content")
        assert isinstance(result, Path)
