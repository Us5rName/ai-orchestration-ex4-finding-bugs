"""Tests for GraphService facade."""

from pathlib import Path

from ex04.services.graph.service import GraphService
from ex04.shared.types import Entity, GraphData, Relationship


class _Runner:
    def execute(self, target_path: str) -> Path:
        return Path(target_path) / "graphify-out" / "graph.json"


class _Parser:
    def parse(self, graph_path: Path) -> GraphData:
        return GraphData(
            entities=[Entity("a", "function"), Entity("b", "function")],
            relationships=[Relationship("a", "b", "calls")],
        )


def test_graph_service_delegates_extract_and_parse() -> None:
    service = GraphService(runner=_Runner(), parser=_Parser())
    graph_path = service.extract("/tmp/code")
    graph = service.parse(graph_path)
    assert graph_path == Path("/tmp/code/graphify-out/graph.json")
    assert [entity.name for entity in graph.entities] == ["a", "b"]


def test_graph_service_returns_analysis_keys() -> None:
    service = GraphService()
    graph = GraphData(
        entities=[Entity("a", "function"), Entity("b", "function")],
        relationships=[Relationship("a", "b", "calls")],
    )
    result = service.analyze(graph)
    assert set(result) == {"god_nodes", "centrality_ranking", "communities"}
