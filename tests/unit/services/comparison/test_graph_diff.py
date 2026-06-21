"""Tests for T6.09 graph-diff comparison reporting."""

from __future__ import annotations

import json
from pathlib import Path

from ex04.services.comparison.graph_diff import (
    GraphDiffer,
    PostGraphStatus,
    diff_graphs,
    render_graph_diff,
)
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
    weight: float | None = None,
) -> Relationship:
    return Relationship(source=source, target=target, type=rel_type, weight=weight)


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
