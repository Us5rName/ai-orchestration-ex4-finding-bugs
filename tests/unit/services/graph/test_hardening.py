"""Hardening tests for H1 (immutable snapshots) and H2 (parser integrity).

Traceability: [TODO T4.19a], [TODO T4.19], [PLAN ADR-007].
"""

from __future__ import annotations

import json
import tempfile
from pathlib import Path
from types import MappingProxyType

import pytest

from ex04.services.graph.parser import GraphParser, GraphParserError
from ex04.services.graph.reader import GraphDataParser, GraphReader
from ex04.services.graph.reader_models import EntityView, RelationshipView
from ex04.shared.types import Entity, GraphData, Relationship

# ---------------------------------------------------------------------------
# helpers
# ---------------------------------------------------------------------------


def _e(name: str, label: str = "", community: int | None = None) -> Entity:
    return Entity(name=name, kind="class", label=label or name, community=community)


def _r(src: str, tgt: str, rel_type: str = "calls", key: str = "") -> Relationship:
    return Relationship(source=src, target=tgt, type=rel_type, key=key or f"{src}:{rel_type}:{tgt}")


def _graph(*entities: Entity, rels: list[Relationship] | None = None) -> GraphData:
    return GraphData(entities=list(entities), relationships=rels or [])


def _write_tmp(payload: dict) -> Path:
    with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
        json.dump(payload, f)
        return Path(f.name)


# ---------------------------------------------------------------------------
# H1 — Immutable GraphReader snapshots and stable identity
# ---------------------------------------------------------------------------


class TestImmutableSnapshots:
    def test_entity_view_is_frozen(self) -> None:
        reader = GraphReader(_graph(_e("a")))
        ev = reader.node("a")
        assert ev is not None
        with pytest.raises((AttributeError, TypeError)):
            ev.entity_id = "other"  # type: ignore[misc]

    def test_original_mutation_does_not_change_reader(self) -> None:
        entity = _e("a")
        gd = _graph(entity)
        reader = GraphReader(gd)
        entity.kind = "mutated"
        gd.entities.append(_e("z"))
        assert reader.node("a") is not None
        assert reader.node("a").kind == "class"  # type: ignore[union-attr]
        assert reader.node("z") is None

    def test_metadata_mutation_does_not_change_reader(self) -> None:
        entity = Entity(name="m", kind="fn", metadata={"x": 1})
        reader = GraphReader(_graph(entity))
        entity.metadata["x"] = 99
        ev = reader.node("m")
        assert ev is not None
        assert ev.metadata["x"] == 1

    def test_returned_metadata_is_immutable(self) -> None:
        entity = Entity(name="m", kind="fn", metadata={"k": "v"})
        reader = GraphReader(_graph(entity))
        ev = reader.node("m")
        assert ev is not None
        assert isinstance(ev.metadata, MappingProxyType)
        with pytest.raises(TypeError):
            ev.metadata["new"] = "value"  # type: ignore[index]

    def test_all_nodes_returns_entity_views(self) -> None:
        reader = GraphReader(_graph(_e("a"), _e("b")))
        for node in reader.all_nodes():
            assert isinstance(node, EntityView)

    def test_edges_of_returns_relationship_views(self) -> None:
        rels = [_r("a", "b")]
        reader = GraphReader(_graph(_e("a"), _e("b"), rels=rels))
        for edge in reader.edges_of("a"):
            assert isinstance(edge, RelationshipView)

    def test_relationship_view_is_frozen(self) -> None:
        rels = [_r("a", "b")]
        reader = GraphReader(_graph(_e("a"), _e("b"), rels=rels))
        rv = reader.edges_of("a")[0]
        with pytest.raises((AttributeError, TypeError)):
            rv.rel_type = "other"  # type: ignore[misc]

    def test_original_rel_mutation_does_not_change_reader(self) -> None:
        rel = _r("a", "b", "calls")
        reader = GraphReader(_graph(_e("a"), _e("b"), rels=[rel]))
        rel.type = "mutated"
        assert reader.edges_of("a")[0].rel_type == "calls"

    def test_stable_id_differs_from_label(self) -> None:
        entity = Entity(name="stable_id", kind="fn", label="Display Label")
        reader = GraphReader(_graph(entity))
        ev = reader.node("stable_id")
        assert ev is not None
        assert ev.entity_id == "stable_id"
        assert ev.label == "Display Label"
        assert ev.entity_id != ev.label

    def test_duplicate_labels_distinct_ids_valid(self) -> None:
        e1 = Entity(name="id_1", kind="fn", label="Duplicate")
        e2 = Entity(name="id_2", kind="fn", label="Duplicate")
        reader = GraphReader(_graph(e1, e2))
        assert reader.node("id_1") is not None
        assert reader.node("id_2") is not None

    def test_id_lookup_uses_stable_id_not_label(self) -> None:
        entity = Entity(name="stable", kind="fn", label="LabelName")
        reader = GraphReader(_graph(entity))
        assert reader.node("LabelName") is None
        assert reader.node("stable") is not None

    def test_directed_and_parallel_remain_distinct(self) -> None:
        rels = [
            Relationship(source="a", target="b", type="calls", key="k1"),
            Relationship(source="b", target="a", type="calls", key="k2"),
            Relationship(source="a", target="b", type="calls", key="k3"),
        ]
        reader = GraphReader(_graph(_e("a"), _e("b"), rels=rels))
        from ex04.shared.types_graph_enums import EdgeDirection
        out = reader.edges_of("a", direction=EdgeDirection.OUTGOING)
        inc = reader.edges_of("a", direction=EdgeDirection.INCOMING)
        assert len(out) == 2
        assert len(inc) == 1

    def test_indexes_internally_consistent(self) -> None:
        rels = [_r("a", "b"), _r("b", "c")]
        reader = GraphReader(_graph(_e("a"), _e("b"), _e("c"), rels=rels))
        top = reader.top_n_by_degree(3)
        total_degree = sum(d for _, d in top)
        assert total_degree == 4  # each edge counted at both endpoints


# ---------------------------------------------------------------------------
# H2 — Parser validation and stable keys
# ---------------------------------------------------------------------------


class TestParserValidation:
    def test_rejects_none_node_id(self) -> None:
        p = _write_tmp({"nodes": [{"id": None}], "links": []})
        try:
            with pytest.raises(GraphParserError, match="None"):
                GraphParser().parse(p)
        finally:
            p.unlink()

    def test_rejects_empty_node_id(self) -> None:
        p = _write_tmp({"nodes": [{"id": ""}], "links": []})
        try:
            with pytest.raises(GraphParserError):
                GraphParser().parse(p)
        finally:
            p.unlink()

    def test_rejects_duplicate_entity_ids(self) -> None:
        p = _write_tmp({"nodes": [{"id": "a"}, {"id": "a"}], "links": []})
        try:
            with pytest.raises(GraphParserError, match="duplicate"):
                GraphParser().parse(p)
        finally:
            p.unlink()

    def test_rejects_none_source(self) -> None:
        p = _write_tmp({
            "nodes": [{"id": "a"}, {"id": "b"}],
            "links": [{"source": None, "target": "b"}],
        })
        try:
            with pytest.raises(GraphParserError, match="None"):
                GraphParser().parse(p)
        finally:
            p.unlink()

    def test_rejects_none_target(self) -> None:
        p = _write_tmp({
            "nodes": [{"id": "a"}, {"id": "b"}],
            "links": [{"source": "a", "target": None}],
        })
        try:
            with pytest.raises(GraphParserError, match="None"):
                GraphParser().parse(p)
        finally:
            p.unlink()

    def test_rejects_endpoint_not_in_entities(self) -> None:
        p = _write_tmp({
            "nodes": [{"id": "a"}],
            "links": [{"source": "a", "target": "unknown"}],
        })
        try:
            with pytest.raises(GraphParserError, match="unknown"):
                GraphParser().parse(p)
        finally:
            p.unlink()

    def test_rejects_duplicate_explicit_key(self) -> None:
        p = _write_tmp({
            "nodes": [{"id": "a"}, {"id": "b"}],
            "links": [
                {"source": "a", "target": "b", "key": "same"},
                {"source": "a", "target": "b", "key": "same"},
            ],
        })
        try:
            with pytest.raises(GraphParserError, match="duplicate"):
                GraphParser().parse(p)
        finally:
            p.unlink()

    def test_rejects_infinite_confidence_score(self) -> None:
        p = _write_tmp({
            "nodes": [{"id": "a"}, {"id": "b"}],
            "links": [{"source": "a", "target": "b", "confidence_score": float("inf")}],
        })
        try:
            with pytest.raises(GraphParserError, match="finite"):
                GraphParser().parse(p)
        finally:
            p.unlink()

    def test_generated_key_is_content_derived_not_index(self) -> None:
        payload = {
            "nodes": [{"id": "a"}, {"id": "b"}],
            "links": [{"source": "a", "target": "b", "relation": "calls"}],
        }
        p1 = _write_tmp(payload)
        payload2 = {
            "nodes": [{"id": "a"}, {"id": "b"}],
            "links": [
                {"source": "a", "target": "b", "relation": "x"},
                {"source": "a", "target": "b", "relation": "calls"},
            ],
        }
        p2 = _write_tmp(payload2)
        try:
            r1 = GraphParser().parse(p1)
            r2 = GraphParser().parse(p2)
            key1 = r1.relationships[0].key
            key2_calls = r2.relationships[1].key
            assert key1 == key2_calls, "Same canonical edge must produce same key regardless of position"
            assert key1  # key must be non-empty
        finally:
            p1.unlink()
            p2.unlink()


# ---------------------------------------------------------------------------
# H2 — Parser injection protocol
# ---------------------------------------------------------------------------


class TestParserInjection:
    def test_protocol_compatible_parser_is_used(self) -> None:
        fake_data = _graph(_e("injected"))
        calls: list[Path] = []

        class FakeParser:
            def parse(self, path: Path) -> GraphData:
                calls.append(path)
                return fake_data

        p = _write_tmp({"nodes": [], "links": []})
        try:
            reader = GraphReader.from_path(p, parser=FakeParser())
            assert len(calls) == 1
            assert calls[0] == p
            assert reader.node("injected") is not None
        finally:
            p.unlink()

    def test_none_parser_uses_graph_parser(self) -> None:
        p = _write_tmp({"nodes": [{"id": "n1"}], "links": []})
        try:
            reader = GraphReader.from_path(p, parser=None)
            assert reader.node("n1") is not None
        finally:
            p.unlink()

    def test_incompatible_object_uses_graph_parser(self) -> None:
        p = _write_tmp({"nodes": [{"id": "n1"}], "links": []})
        try:
            reader = GraphReader.from_path(p, parser="not-a-parser")
            assert reader.node("n1") is not None
        finally:
            p.unlink()

    def test_isinstance_not_required_for_protocol(self) -> None:
        class FakeParser:
            def parse(self, path: Path) -> GraphData:
                return _graph(_e("from_fake"))

        reader = GraphReader.from_path(Path("/dev/null"), parser=FakeParser())
        assert reader.node("from_fake") is not None

    def test_graph_data_parser_protocol_recognized(self) -> None:
        class Duck:
            def parse(self, path: Path) -> GraphData:
                return GraphData()

        assert isinstance(Duck(), GraphDataParser)
