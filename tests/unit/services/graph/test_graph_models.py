"""Tests for T4.19a enriched Entity, Relationship, and GraphParser.

Covers stable ID vs label, confidence enum, anchors, metadata, parallel
edges, direction preservation, and parser validation. All tests are
keyless and use synthetic in-memory fixtures.
"""

from __future__ import annotations

import json
import tempfile
from pathlib import Path

import pytest

from ex04.services.graph.parser import GraphParser, GraphParserError
from ex04.shared.types import (
    ConfidenceState,
    EdgeDirection,
    Entity,
    Relationship,
)

# ---------------------------------------------------------------------------
# helpers
# ---------------------------------------------------------------------------

def _write_graph(payload: dict) -> Path:
    """Write payload as JSON to a temp file, return path."""
    with tempfile.NamedTemporaryFile(
        mode="w", suffix=".json", delete=False
    ) as f:
        json.dump(payload, f)
        return Path(f.name)


def _minimal_graph(**extra_node_fields: object) -> dict:
    node: dict = {"id": "n1", "label": "NodeOne", "file_type": "class"}
    node.update(extra_node_fields)
    return {"nodes": [node], "links": []}


# ---------------------------------------------------------------------------
# Entity model
# ---------------------------------------------------------------------------

class TestEntityModel:
    """Entity enrichment: stable ID, label, community, metadata."""

    def test_id_alias_for_name(self) -> None:
        e = Entity(name="node_id", kind="class")
        assert e.id == "node_id"

    def test_label_separate_from_id(self) -> None:
        e = Entity(name="node_id", kind="class", label="Display Name")
        assert e.id == "node_id"
        assert e.label == "Display Name"

    def test_duplicate_labels_allowed(self) -> None:
        e1 = Entity(name="id1", kind="class", label="Same")
        e2 = Entity(name="id2", kind="class", label="Same")
        assert e1.id != e2.id
        assert e1.label == e2.label

    def test_community_none_by_default(self) -> None:
        e = Entity(name="x", kind="file")
        assert e.community is None

    def test_community_assigned(self) -> None:
        e = Entity(name="x", kind="file", community=3)
        assert e.community == 3

    def test_metadata_preserved(self) -> None:
        e = Entity(name="x", kind="class", metadata={"custom": "val"})
        assert e.metadata["custom"] == "val"

    def test_immutable_metadata_view(self) -> None:
        e = Entity(name="x", kind="class", metadata={"k": 1})
        view = e.immutable_metadata()
        with pytest.raises((TypeError, AttributeError)):
            view["k"] = 99  # type: ignore[index]

    def test_backward_compat_positional(self) -> None:
        """Existing positional construction still works."""
        e = Entity("my_id", "function")
        assert e.name == "my_id"
        assert e.kind == "function"

    def test_backward_compat_keyword_name(self) -> None:
        e = Entity(name="AuthService", kind="class", file_path="auth.py")
        assert e.name == "AuthService"
        assert e.file_path == "auth.py"


# ---------------------------------------------------------------------------
# Relationship model
# ---------------------------------------------------------------------------

class TestRelationshipModel:
    """Relationship enrichment: key, direction, confidence, metadata."""

    def test_source_id_alias(self) -> None:
        r = Relationship(source="a", target="b", type="calls")
        assert r.source_id == "a"

    def test_target_id_alias(self) -> None:
        r = Relationship(source="a", target="b", type="calls")
        assert r.target_id == "b"

    def test_rel_type_alias(self) -> None:
        r = Relationship(source="a", target="b", type="inherits")
        assert r.rel_type == "inherits"

    def test_missing_confidence_is_unknown(self) -> None:
        r = Relationship(source="a", target="b")
        assert r.confidence_state is ConfidenceState.UNKNOWN

    def test_extracted_confidence(self) -> None:
        r = Relationship(source="a", target="b", confidence="extracted")
        assert r.confidence_state is ConfidenceState.EXTRACTED

    def test_inferred_confidence(self) -> None:
        r = Relationship(source="a", target="b", confidence="inferred")
        assert r.confidence_state is ConfidenceState.INFERRED

    def test_invalid_confidence_maps_to_unknown(self) -> None:
        r = Relationship(source="a", target="b", confidence="bogus")
        assert r.confidence_state is ConfidenceState.UNKNOWN

    def test_confidence_score_preserved(self) -> None:
        r = Relationship(source="a", target="b", confidence_score=0.9)
        assert r.confidence_score == pytest.approx(0.9)

    def test_weight_preserved(self) -> None:
        r = Relationship(source="a", target="b", weight=2.5)
        assert r.weight == pytest.approx(2.5)

    def test_source_anchor_preserved(self) -> None:
        r = Relationship(source="a", target="b", source_anchor="auth.py:10-20")
        assert r.source_anchor == "auth.py:10-20"

    def test_metadata_preserved(self) -> None:
        r = Relationship(source="a", target="b", metadata={"via": "infer"})
        assert r.metadata["via"] == "infer"

    def test_key_distinguishes_parallel_edges(self) -> None:
        r1 = Relationship(source="a", target="b", type="calls", key="k1")
        r2 = Relationship(source="a", target="b", type="calls", key="k2")
        assert r1.key != r2.key

    def test_backward_compat_positional(self) -> None:
        r = Relationship("a", "b", "calls")
        assert r.source == "a"
        assert r.target == "b"
        assert r.type == "calls"


# ---------------------------------------------------------------------------
# GraphParser enrichment
# ---------------------------------------------------------------------------

class TestGraphParserEnrichment:
    """Parser populates all T4.19a fields correctly."""

    def test_minimal_valid_graph(self) -> None:
        p = _write_graph({"nodes": [{"id": "n1", "file_type": "class"}], "links": []})
        result = GraphParser().parse(p)
        p.unlink()
        assert len(result.entities) == 1
        assert result.entities[0].id == "n1"

    def test_label_separate_from_id(self) -> None:
        p = _write_graph({"nodes": [
            {"id": "node_1", "label": "Pretty Name", "file_type": "class"}
        ], "links": []})
        result = GraphParser().parse(p)
        p.unlink()
        e = result.entities[0]
        assert e.id == "node_1"
        assert e.label == "Pretty Name"

    def test_duplicate_display_labels(self) -> None:
        p = _write_graph({"nodes": [
            {"id": "a", "label": "Dup", "file_type": "class"},
            {"id": "b", "label": "Dup", "file_type": "class"},
        ], "links": []})
        result = GraphParser().parse(p)
        p.unlink()
        labels = [e.label for e in result.entities]
        ids = [e.id for e in result.entities]
        assert labels == ["Dup", "Dup"]
        assert ids[0] != ids[1]

    def test_community_assigned_from_node(self) -> None:
        p = _write_graph({"nodes": [
            {"id": "n1", "file_type": "class", "community": 5}
        ], "links": []})
        result = GraphParser().parse(p)
        p.unlink()
        assert result.entities[0].community == 5

    def test_metadata_preserved_on_node(self) -> None:
        p = _write_graph({"nodes": [
            {"id": "n1", "file_type": "class", "custom_key": "cval"}
        ], "links": []})
        result = GraphParser().parse(p)
        p.unlink()
        assert result.entities[0].metadata.get("custom_key") == "cval"

    def test_missing_confidence_none(self) -> None:
        p = _write_graph({"nodes": [{"id": "a"}, {"id": "b"}], "links": [
            {"source": "a", "target": "b", "relation": "calls"}
        ]})
        result = GraphParser().parse(p)
        p.unlink()
        assert result.relationships[0].confidence is None
        assert result.relationships[0].confidence_state is ConfidenceState.UNKNOWN

    def test_valid_confidence_preserved(self) -> None:
        p = _write_graph({"nodes": [{"id": "a"}, {"id": "b"}], "links": [
            {"source": "a", "target": "b", "confidence": "extracted"}
        ]})
        result = GraphParser().parse(p)
        p.unlink()
        assert result.relationships[0].confidence == "extracted"

    def test_invalid_confidence_raises(self) -> None:
        p = _write_graph({"nodes": [{"id": "a"}, {"id": "b"}], "links": [
            {"source": "a", "target": "b", "confidence": "CERTAIN"}
        ]})
        with pytest.raises(GraphParserError, match="confidence"):
            GraphParser().parse(p)
        p.unlink()

    def test_confidence_score_preserved(self) -> None:
        p = _write_graph({"nodes": [{"id": "a"}, {"id": "b"}], "links": [
            {"source": "a", "target": "b", "confidence_score": 0.75}
        ]})
        result = GraphParser().parse(p)
        p.unlink()
        assert result.relationships[0].confidence_score == pytest.approx(0.75)

    def test_invalid_numeric_field_raises(self) -> None:
        p = _write_graph({"nodes": [{"id": "a"}, {"id": "b"}], "links": [
            {"source": "a", "target": "b", "weight": "not_a_number"}
        ]})
        with pytest.raises(GraphParserError, match="weight"):
            GraphParser().parse(p)
        p.unlink()

    def test_missing_endpoint_raises(self) -> None:
        p = _write_graph({"nodes": [{"id": "a"}], "links": [
            {"source": "a", "target": "", "relation": "calls"}
        ]})
        with pytest.raises(GraphParserError, match="target"):
            GraphParser().parse(p)
        p.unlink()

    def test_parallel_relationships_preserved(self) -> None:
        p = _write_graph({"nodes": [{"id": "a"}, {"id": "b"}], "links": [
            {"source": "a", "target": "b", "relation": "calls", "key": "k1"},
            {"source": "a", "target": "b", "relation": "calls", "key": "k2"},
        ]})
        result = GraphParser().parse(p)
        p.unlink()
        assert len(result.relationships) == 2
        keys = {r.key for r in result.relationships}
        assert keys == {"k1", "k2"}

    def test_typed_source_anchor_preserved(self) -> None:
        p = _write_graph({"nodes": [{"id": "a"}, {"id": "b"}], "links": [
            {"source": "a", "target": "b", "source_anchor": "auth.py:10-20"}
        ]})
        result = GraphParser().parse(p)
        p.unlink()
        assert result.relationships[0].source_anchor == "auth.py:10-20"

    def test_stable_relationship_key_auto_generated(self) -> None:
        """Key is generated when not explicitly provided."""
        p = _write_graph({"nodes": [{"id": "a"}, {"id": "b"}], "links": [
            {"source": "a", "target": "b", "relation": "calls"},
        ]})
        result = GraphParser().parse(p)
        p.unlink()
        assert result.relationships[0].key != ""

    def test_malformed_graph_structure_raises(self) -> None:
        p = _write_graph({"nodes": "not_a_list", "links": []})
        with pytest.raises(GraphParserError):
            GraphParser().parse(p)
        p.unlink()


# ---------------------------------------------------------------------------
# EdgeDirection enum
# ---------------------------------------------------------------------------

class TestEdgeDirection:
    """EdgeDirection is a usable string enum."""

    def test_values_exist(self) -> None:
        assert EdgeDirection.OUTGOING.value == "outgoing"
        assert EdgeDirection.INCOMING.value == "incoming"
        assert EdgeDirection.BOTH.value == "both"

    def test_equality(self) -> None:
        assert EdgeDirection.BOTH is EdgeDirection.BOTH
