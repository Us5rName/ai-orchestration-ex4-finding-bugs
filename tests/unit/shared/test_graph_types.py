"""Tests for shared graph types — Entity, Relationship, Community, GraphData."""

from ex04.shared import (
    Community,
    Entity,
    GraphData,
    Relationship,
)


class TestEntity:
    """Tests for the Entity dataclass."""

    def test_entity_requires_name_and_kind(self) -> None:
        entity = Entity(name="my_func", kind="function")
        assert entity.name == "my_func"
        assert entity.kind == "function"
        assert entity.file_path == ""
        assert entity.line_range == (0, 0)

    def test_entity_with_all_fields(self) -> None:
        entity = Entity(name="my_class", kind="class", file_path="app.py", line_range=(1, 50))
        assert entity.name == "my_class"
        assert entity.kind == "class"
        assert entity.file_path == "app.py"
        assert entity.line_range == (1, 50)


class TestRelationship:
    """Tests for the Relationship dataclass."""

    def test_relationship_requires_source_and_target(self) -> None:
        rel = Relationship(source="a", target="b")
        assert rel.source == "a"
        assert rel.target == "b"
        assert rel.type == ""

    def test_relationship_with_type(self) -> None:
        rel = Relationship(source="a", target="b", type="calls")
        assert rel.type == "calls"


class TestCommunity:
    """Tests for the Community dataclass."""

    def test_community_requires_name(self) -> None:
        comm = Community(name="cluster_1")
        assert comm.name == "cluster_1"
        assert comm.entities == []
        assert comm.size == 0

    def test_community_with_entities(self) -> None:
        comm = Community(name="cluster_1", entities=["a", "b"], size=2)
        assert comm.entities == ["a", "b"]
        assert comm.size == 2


class TestGraphData:
    """Tests for the GraphData dataclass."""

    def test_graph_data_empty(self) -> None:
        graph = GraphData()
        assert graph.entities == []
        assert graph.relationships == []
        assert graph.communities == []

    def test_graph_data_with_content(self) -> None:
        entity = Entity(name="x", kind="function")
        rel = Relationship(source="x", target="y", type="calls")
        comm = Community(name="c1", entities=["x"], size=1)
        graph = GraphData(entities=[entity], relationships=[rel], communities=[comm])
        assert len(graph.entities) == 1
        assert len(graph.relationships) == 1
        assert len(graph.communities) == 1
