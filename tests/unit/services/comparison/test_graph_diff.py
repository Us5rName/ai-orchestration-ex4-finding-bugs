"""Tests for T6.09 graph-diff comparison reporting."""

from __future__ import annotations

import json
from pathlib import Path

from ex04.services.comparison.graph_diff import (
    GraphDiffer,
    PostGraphStatus,
    diff_graph_data,
    diff_graphs,
    render_graph_diff,
)
from ex04.services.comparison.graph_diff.canonicalize import canonical_graph_hash
from ex04.services.graph.interface import build_graph_reader
from ex04.shared.artifact_store import ArtifactOverwriteError
from ex04.shared.types import Entity, GraphData, Relationship


def _entity(
    name: str,
    *,
    label: str = "",
    community: int | None = None,
    kind: str = "function",
    metadata: dict[str, object] | None = None,
) -> Entity:
    return Entity(
        name=name,
        label=label or name,
        kind=kind,
        file_path=f"{name}.py",
        line_range=(1, 2),
        community=community,
        metadata=metadata or {},
    )


def _rel(
    source: str,
    target: str,
    *,
    rel_type: str = "calls",
    key: str = "",
    confidence: str | None = None,
    weight: float | None = None,
) -> Relationship:
    return Relationship(
        source=source,
        target=target,
        type=rel_type,
        key=key,
        confidence=confidence,
        weight=weight,
    )


def test_changed_graph_classifies_entities_relationships_and_communities() -> None:
    before = GraphData(
        entities=[_entity("a", community=1), _entity("b", community=1), _entity("c", community=2)],
        relationships=[_rel("a", "b", weight=0.5), _rel("b", "c")],
    )
    after = GraphData(
        entities=[
            _entity("a", community=9),
            _entity("b", community=None, metadata={"role": "changed"}),
            _entity("d", community=3),
        ],
        relationships=[_rel("a", "b", weight=0.9), _rel("a", "d")],
    )

    result = diff_graphs(before, after)

    entity_changes = {(c.entity_id, c.change.value) for c in result.entity_changes}
    assert ("b", "changed") in entity_changes
    assert ("c", "removed") in entity_changes
    assert ("d", "added") in entity_changes
    relationship_changes = {
        (c.identity.source_id, c.identity.target_id, c.change.value)
        for c in result.relationship_changes
    }
    assert ("a", "b", "changed") in relationship_changes
    assert ("b", "c", "removed") in relationship_changes
    assert ("a", "d", "added") in relationship_changes
    assert {c.change.value for c in result.community_changes} >= {"contracted", "removed", "added"}


def test_unchanged_graph_includes_unchanged_classifications() -> None:
    graph = GraphData(
        entities=[_entity("a", community=1), _entity("b", community=1)],
        relationships=[_rel("a", "b", weight=1.0)],
    )

    result = GraphDiffer(graph, graph).compute()

    assert result.status is PostGraphStatus.UNCHANGED
    assert [c.change.value for c in result.entity_changes] == ["unchanged", "unchanged"]
    assert [c.change.value for c in result.relationship_changes] == ["unchanged"]
    assert [c.change.value for c in result.community_changes] == ["preserved"]


def test_missing_post_graph_returns_typed_status() -> None:
    result = diff_graphs(GraphData(entities=[_entity("a")]), None)

    assert result.status is PostGraphStatus.MISSING
    assert result.entity_changes == ()
    assert "post-fix graph" in result.error_detail


def test_invalid_post_graph_returns_typed_status() -> None:
    result = diff_graphs(GraphData(), object())  # type: ignore[arg-type]

    assert result.status is PostGraphStatus.INVALID
    assert "GraphData" in result.error_detail


def test_community_matching_uses_membership_not_raw_ids() -> None:
    before = GraphData(
        entities=[_entity("a", community=1), _entity("b", community=1)],
        relationships=[],
    )
    after = GraphData(
        entities=[_entity("a", community=99), _entity("b", community=99)],
        relationships=[],
    )

    result = diff_graphs(before, after)

    assert len(result.community_changes) == 1
    assert result.community_changes[0].change.value == "preserved"
    assert result.community_changes[0].before_community == "1"
    assert result.community_changes[0].after_community == "99"


def test_result_order_is_deterministic() -> None:
    before = GraphData(entities=[_entity("b"), _entity("a")], relationships=[_rel("b", "a")])
    after = GraphData(entities=[_entity("c"), _entity("a")], relationships=[_rel("a", "c")])

    first = diff_graphs(before, after)
    second = diff_graphs(before, after)

    assert first.to_dict() == second.to_dict()


def test_artifacts_are_written_with_hashes(tmp_path: Path) -> None:
    before = GraphData(entities=[_entity("a")], relationships=[])
    after = GraphData(entities=[_entity("a"), _entity("b")], relationships=[])
    result = diff_graphs(before, after)

    artifacts = render_graph_diff(result, tmp_path)

    assert artifacts.json_path == tmp_path / "reports" / "graph_diff.json"
    assert artifacts.markdown_path == tmp_path / "reports" / "graph_diff.md"
    assert len(artifacts.graph_diff_hash) == 64
    assert json.loads(artifacts.json_path.read_text(encoding="utf-8"))["status"] == "available"
    assert "Graph Diff" in artifacts.markdown_path.read_text(encoding="utf-8")


def test_parallel_relationships_are_not_collapsed() -> None:
    before = GraphData(
        entities=[_entity("a"), _entity("b")],
        relationships=[
            _rel("a", "b", key="1", weight=0.1),
            _rel("a", "b", key="2", weight=0.2),
        ],
    )
    after = GraphData(
        entities=[_entity("a"), _entity("b")],
        relationships=[
            _rel("a", "b", key="2", weight=0.3),
            _rel("a", "b", key="1", weight=0.1),
            _rel("a", "b", key="3", weight=0.4),
        ],
    )

    result = diff_graph_data(before, after)

    changes = [change.change.value for change in result.relationship_changes]
    assert changes.count("unchanged") == 1
    assert changes.count("changed") == 1
    assert changes.count("added") == 1


def test_graph_hash_is_order_independent() -> None:
    first = GraphData(
        entities=[_entity("a"), _entity("b")],
        relationships=[_rel("a", "b", key="1"), _rel("b", "a", key="2")],
    )
    second = GraphData(
        entities=[_entity("b"), _entity("a")],
        relationships=[_rel("b", "a", key="2"), _rel("a", "b", key="1")],
    )

    assert canonical_graph_hash(build_graph_reader(first)) == canonical_graph_hash(
        build_graph_reader(second)
    )


def test_one_to_one_partial_community_replacement_is_reorganized() -> None:
    before = GraphData(
        entities=[
            _entity("a", community=1),
            _entity("b", community=1),
            _entity("c", community=1),
        ],
    )
    after = GraphData(
        entities=[
            _entity("a", community=9),
            _entity("b", community=9),
            _entity("d", community=9),
        ],
    )

    result = diff_graphs(before, after)

    assert [change.change.value for change in result.community_changes] == ["reorganized"]


def test_blocked_status_keeps_pre_snapshot() -> None:
    result = diff_graphs(
        GraphData(entities=[_entity("a")]),
        None,
        post_graph_status=PostGraphStatus.BLOCKED,
        post_graph_error="generation prerequisite failed",
    )

    assert result.status is PostGraphStatus.BLOCKED
    assert result.pre_snapshot.entity_count == 1
    assert "prerequisite" in result.error_detail


def test_graph_diff_artifacts_are_write_once(tmp_path: Path) -> None:
    result = diff_graphs(GraphData(entities=[_entity("a")]), None)
    render_graph_diff(result, tmp_path)
    (tmp_path / "reports" / "graph_diff.json").write_text("different", encoding="utf-8")

    try:
        render_graph_diff(result, tmp_path)
    except ArtifactOverwriteError:
        pass
    else:
        raise AssertionError("expected immutable artifact conflict")
