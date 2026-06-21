"""Tests for shared graph operations."""

from __future__ import annotations

from ex04.shared.graph_ops import connected_components, degree_map
from ex04.shared.types import Entity, Relationship


def test_degree_map_counts_undirected_relationships() -> None:
    relationships = [
        Relationship(source="a", target="b"),
        Relationship(source="a", target="c"),
        Relationship(source="c", target="a"),
    ]

    assert degree_map(relationships) == {"a": 3, "b": 1, "c": 2}


def test_connected_components_include_entity_and_edge_only_nodes() -> None:
    entities = [Entity(name="a", kind="class"), Entity(name="isolated", kind="file")]
    relationships = [
        Relationship(source="a", target="b"),
        Relationship(source="c", target="d"),
    ]

    assert connected_components(entities, relationships) == [
        ["a", "b"],
        ["c", "d"],
        ["isolated"],
    ]
