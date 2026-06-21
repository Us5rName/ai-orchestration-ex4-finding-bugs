"""GraphDiff engine consuming canonical GraphReader snapshots."""

from __future__ import annotations

from ex04.services.comparison.graph_diff.canonicalize import (
    entity_attributes,
    field_changes,
)
from ex04.services.comparison.graph_diff.community_matcher import classify_communities
from ex04.services.comparison.graph_diff.models import (
    CommunityChangeType,
    EntityChange,
    EntityChangeType,
    GraphDiffResult,
    PostGraphStatus,
    RelationshipChange,
    RelationshipChangeType,
)
from ex04.services.comparison.graph_diff.relationship_matcher import relationship_changes
from ex04.services.comparison.graph_diff.snapshots import snapshot_ref
from ex04.services.graph.interface import GraphReaderInterface, build_graph_reader
from ex04.shared.types import GraphData


class GraphDiffer:
    """Deterministic pre/post graph comparison engine."""

    def __init__(
        self,
        before: GraphReaderInterface | GraphData,
        after: GraphReaderInterface | GraphData,
    ) -> None:
        self._before = build_graph_reader(before) if isinstance(before, GraphData) else before
        self._after = build_graph_reader(after) if isinstance(after, GraphData) else after

    def compute(self) -> GraphDiffResult:
        """Return complete typed classifications for entities, edges, communities."""
        entity_changes = self._entity_changes()
        relationship_changes = self._relationship_changes()
        community_changes = classify_communities(self._before, self._after)
        changed = (
            any(c.change is not EntityChangeType.UNCHANGED for c in entity_changes)
            or any(c.change is not RelationshipChangeType.UNCHANGED for c in relationship_changes)
            or any(c.change is not CommunityChangeType.PRESERVED for c in community_changes)
        )
        return GraphDiffResult(
            status=PostGraphStatus.AVAILABLE if changed else PostGraphStatus.UNCHANGED,
            pre_snapshot=snapshot_ref(self._before),
            post_snapshot=snapshot_ref(self._after),
            entity_changes=entity_changes,
            relationship_changes=relationship_changes,
            community_changes=community_changes,
        )

    def _entity_changes(self) -> tuple[EntityChange, ...]:
        before = {entity.entity_id: entity for entity in self._before.all_nodes()}
        after = {entity.entity_id: entity for entity in self._after.all_nodes()}
        changes = []
        for entity_id in sorted(before.keys() | after.keys()):
            before_attrs = entity_attributes(before[entity_id]) if entity_id in before else ()
            after_attrs = entity_attributes(after[entity_id]) if entity_id in after else ()
            if entity_id not in before:
                change = EntityChangeType.ADDED
            elif entity_id not in after:
                change = EntityChangeType.REMOVED
            else:
                change = EntityChangeType.UNCHANGED if before_attrs == after_attrs else EntityChangeType.CHANGED
            changes.append(
                EntityChange(
                    entity_id,
                    change,
                    before_attrs,
                    after_attrs,
                    field_changes(before_attrs, after_attrs),
                )
            )
        return tuple(changes)

    def _relationship_changes(self) -> tuple[RelationshipChange, ...]:
        return relationship_changes(self._before, self._after)


def diff_readers(before: GraphReaderInterface, after: GraphReaderInterface) -> GraphDiffResult:
    """Diff two canonical reader snapshots."""
    return GraphDiffer(before, after).compute()


def diff_graph_data(before: GraphData, after: GraphData) -> GraphDiffResult:
    """Construct readers from GraphData and delegate to diff_readers."""
    return diff_readers(build_graph_reader(before), build_graph_reader(after))


def diff_graphs(
    before: GraphData | None,
    after: GraphData | None,
    *,
    post_graph_status: PostGraphStatus | None = None,
    post_graph_error: str = "",
) -> GraphDiffResult:
    """Compute graph diff with reachable missing/invalid/blocked states."""
    if before is None:
        return GraphDiffResult(PostGraphStatus.MISSING, error_detail="pre-fix graph snapshot is missing")
    pre_reader = build_graph_reader(before)
    pre_snapshot = snapshot_ref(pre_reader)
    if post_graph_status is PostGraphStatus.BLOCKED:
        return GraphDiffResult(PostGraphStatus.BLOCKED, pre_snapshot=pre_snapshot, error_detail=post_graph_error)
    if post_graph_status is PostGraphStatus.INVALID:
        return GraphDiffResult(PostGraphStatus.INVALID, pre_snapshot=pre_snapshot, error_detail=post_graph_error)
    if after is None:
        return GraphDiffResult(PostGraphStatus.MISSING, pre_snapshot=pre_snapshot, error_detail="post-fix graph snapshot is missing")
    if not isinstance(after, GraphData):
        return GraphDiffResult(PostGraphStatus.INVALID, pre_snapshot=pre_snapshot, error_detail="post-fix graph snapshot must be GraphData")
    try:
        return diff_readers(pre_reader, build_graph_reader(after))
    except (TypeError, ValueError, AttributeError) as exc:
        return GraphDiffResult(PostGraphStatus.INVALID, pre_snapshot=pre_snapshot, error_detail=str(exc))
