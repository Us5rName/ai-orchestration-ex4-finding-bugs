"""Tests for GraphReader facade (T4.19).

Covers construction, all public operations, edge cases, immutability,
and deterministic ordering. All tests are keyless and use synthetic
in-memory fixtures.
"""

from __future__ import annotations

import json
import tempfile
from pathlib import Path

import pytest

from ex04.services.graph.parser import GraphParser
from ex04.services.graph.reader import GraphReader
from ex04.shared.types import EdgeDirection, Entity, GraphData, Relationship

# ---------------------------------------------------------------------------
# fixture helpers
# ---------------------------------------------------------------------------

def _e(name: str, kind: str = "class", community: int | None = None) -> Entity:
    return Entity(name=name, kind=kind, community=community)


def _r(src: str, tgt: str, rel_type: str = "calls", key: str = "") -> Relationship:
    k = key or f"{src}:{rel_type}:{tgt}"
    return Relationship(source=src, target=tgt, type=rel_type, key=k)


def _graph(*entities: Entity, rels: list[Relationship] | None = None) -> GraphData:
    return GraphData(entities=list(entities), relationships=rels or [])


def _write_graph(payload: dict) -> Path:
    with tempfile.NamedTemporaryFile(
        mode="w", suffix=".json", delete=False
    ) as f:
        json.dump(payload, f)
        return Path(f.name)


# ---------------------------------------------------------------------------
# construction
# ---------------------------------------------------------------------------

class TestConstruction:
    def test_from_graph_data(self) -> None:
        gd = _graph(_e("a"))
        reader = GraphReader(gd)
        assert reader.node("a") is not None

    def test_from_path_delegates_to_parser(self) -> None:
        p = _write_graph({"nodes": [{"id": "n1", "file_type": "class"}], "links": []})
        reader = GraphReader.from_path(p)
        p.unlink()
        assert reader.node("n1") is not None

    def test_from_path_with_custom_parser(self) -> None:
        p = _write_graph({"nodes": [{"id": "x1"}], "links": []})
        custom = GraphParser()
        reader = GraphReader.from_path(p, parser=custom)
        p.unlink()
        assert reader.node("x1") is not None

    def test_empty_graph(self) -> None:
        reader = GraphReader(_graph())
        assert reader.all_nodes() == ()
        assert reader.top_n_by_degree(5) == ()


# ---------------------------------------------------------------------------
# node()
# ---------------------------------------------------------------------------

class TestNodeLookup:
    def test_known_node_returned(self) -> None:
        reader = GraphReader(_graph(_e("a"), _e("b")))
        assert reader.node("a") is not None
        assert reader.node("a").name == "a"  # type: ignore[union-attr]

    def test_unknown_node_returns_none(self) -> None:
        reader = GraphReader(_graph(_e("a")))
        assert reader.node("z") is None

    def test_uses_stable_id_not_label(self) -> None:
        e = Entity(name="stable_id", kind="class", label="Display")
        reader = GraphReader(_graph(e))
        assert reader.node("stable_id") is not None
        assert reader.node("Display") is None


# ---------------------------------------------------------------------------
# all_nodes()
# ---------------------------------------------------------------------------

class TestAllNodes:
    def test_deterministic_alpha_order(self) -> None:
        reader = GraphReader(_graph(_e("c"), _e("a"), _e("b")))
        ids = [n.id for n in reader.all_nodes()]
        assert ids == ["a", "b", "c"]

    def test_empty_graph_empty_tuple(self) -> None:
        assert GraphReader(_graph()).all_nodes() == ()

    def test_isolated_node_included(self) -> None:
        reader = GraphReader(_graph(_e("lonely")))
        assert len(reader.all_nodes()) == 1

    def test_result_is_tuple(self) -> None:
        reader = GraphReader(_graph(_e("a")))
        result = reader.all_nodes()
        assert isinstance(result, tuple)


# ---------------------------------------------------------------------------
# edges_of()
# ---------------------------------------------------------------------------

class TestEdgesOf:
    def _reader(self) -> GraphReader:
        rels = [
            _r("a", "b", "calls", "k1"),
            _r("c", "a", "imports", "k2"),
            _r("a", "a", "self_loop", "k3"),
        ]
        return GraphReader(_graph(_e("a"), _e("b"), _e("c"), rels=rels))

    def test_outgoing(self) -> None:
        r = self._reader()
        edges = r.edges_of("a", direction=EdgeDirection.OUTGOING)
        types = {e.type for e in edges}
        assert "calls" in types
        assert "self_loop" in types
        assert "imports" not in types

    def test_incoming(self) -> None:
        r = self._reader()
        edges = r.edges_of("a", direction=EdgeDirection.INCOMING)
        types = {e.type for e in edges}
        assert "imports" in types
        assert "self_loop" in types
        assert "calls" not in types

    def test_both_incident(self) -> None:
        r = self._reader()
        edges = r.edges_of("a")
        types = {e.type for e in edges}
        assert {"calls", "imports", "self_loop"} == types

    def test_unknown_node_returns_empty(self) -> None:
        r = self._reader()
        assert r.edges_of("unknown") == ()

    def test_result_is_tuple(self) -> None:
        r = self._reader()
        assert isinstance(r.edges_of("a"), tuple)

    def test_parallel_relationships_all_returned(self) -> None:
        rels = [
            _r("a", "b", "calls", "k1"),
            _r("a", "b", "calls", "k2"),
        ]
        reader = GraphReader(_graph(_e("a"), _e("b"), rels=rels))
        edges = reader.edges_of("a", direction=EdgeDirection.OUTGOING)
        assert len(edges) == 2

    def test_default_direction_is_both(self) -> None:
        rels = [_r("a", "b", "calls", "k1"), _r("c", "a", "imports", "k2")]
        reader = GraphReader(_graph(_e("a"), _e("b"), _e("c"), rels=rels))
        both = reader.edges_of("a")
        assert len(both) == 2

    def test_direction_preserved(self) -> None:
        rels = [_r("a", "b", "calls", "k1")]
        reader = GraphReader(_graph(_e("a"), _e("b"), rels=rels))
        assert len(reader.edges_of("a", direction=EdgeDirection.OUTGOING)) == 1
        assert len(reader.edges_of("b", direction=EdgeDirection.OUTGOING)) == 0
        assert len(reader.edges_of("b", direction=EdgeDirection.INCOMING)) == 1


# ---------------------------------------------------------------------------
# top_n_by_degree()
# ---------------------------------------------------------------------------

class TestTopNByDegree:
    def _reader(self) -> GraphReader:
        rels = [
            _r("a", "b", key="k1"), _r("a", "c", key="k2"),
            _r("b", "c", key="k3"),
        ]
        return GraphReader(_graph(_e("a"), _e("b"), _e("c"), rels=rels))

    def test_top_1(self) -> None:
        r = self._reader()
        top = r.top_n_by_degree(1)
        assert len(top) == 1
        assert top[0][0].id == "a"  # degree 2 (out:2)

    def test_n_zero_returns_empty(self) -> None:
        assert self._reader().top_n_by_degree(0) == ()

    def test_n_negative_raises(self) -> None:
        with pytest.raises(ValueError):
            self._reader().top_n_by_degree(-1)

    def test_n_larger_than_graph_returns_all(self) -> None:
        r = self._reader()
        top = r.top_n_by_degree(100)
        assert len(top) == 3

    def test_returns_tuple_of_entity_degree_pairs(self) -> None:
        from ex04.services.graph.reader_models import EntityView
        r = self._reader()
        top = r.top_n_by_degree(2)
        assert isinstance(top, tuple)
        for pair in top:
            assert isinstance(pair[0], EntityView)
            assert isinstance(pair[1], int)

    def test_tie_breaking_by_id(self) -> None:
        # All three nodes a, b, c have degree 2; tie-break by stable ID asc.
        r = self._reader()
        ids = [pair[0].id for pair in r.top_n_by_degree(3)]
        # With identical degree, order must be alphabetical (a, b, c).
        assert ids == sorted(ids)
        # And the result must be deterministic across calls.
        assert ids == [pair[0].id for pair in r.top_n_by_degree(3)]

    def test_isolated_node_degree_zero(self) -> None:
        reader = GraphReader(_graph(_e("x")))
        top = reader.top_n_by_degree(1)
        assert top[0][1] == 0

    def test_repeated_calls_identical(self) -> None:
        r = self._reader()
        assert r.top_n_by_degree(3) == r.top_n_by_degree(3)


# ---------------------------------------------------------------------------
# communities()
# ---------------------------------------------------------------------------

class TestCommunities:
    def test_grouped_by_community(self) -> None:
        reader = GraphReader(_graph(
            _e("a", community=1), _e("b", community=1), _e("c", community=2)
        ))
        comms = reader.communities()
        assert "1" in comms
        assert "2" in comms
        assert len(comms["1"]) == 2

    def test_none_community_key(self) -> None:
        reader = GraphReader(_graph(_e("x")))  # community=None by default
        comms = reader.communities()
        assert None in comms

    def test_result_is_immutable(self) -> None:
        reader = GraphReader(_graph(_e("a", community=1)))
        comms = reader.communities()
        with pytest.raises((TypeError, AttributeError)):
            comms["new_key"] = ()  # type: ignore[index]

    def test_entities_in_stable_order(self) -> None:
        reader = GraphReader(_graph(
            _e("c", community=1), _e("a", community=1), _e("b", community=1)
        ))
        comms = reader.communities()
        ids = [e.id for e in comms["1"]]
        assert ids == sorted(ids)

    def test_empty_graph_empty_communities(self) -> None:
        comms = GraphReader(_graph()).communities()
        assert len(comms) == 0 or all(len(v) == 0 for v in comms.values())
