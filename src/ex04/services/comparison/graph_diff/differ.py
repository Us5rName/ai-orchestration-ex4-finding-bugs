"""GraphDiff engine consuming shared GraphData snapshots."""

from __future__ import annotations

from ex04.services.comparison.graph_diff.canonicalize import (
    entity_attributes,
    relationship_attributes,
    relationship_identity,
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
    RelationshipIdentity,
)
from ex04.shared.types import GraphData


class GraphDiffer:
    """Deterministic pre/post graph comparison engine."""

    def __init__(self, before: GraphData, after: GraphData) -> None:
        self._before = before
        self._after = after

    def compute(self) -> GraphDiffResult:
        """Return complete typed classifications for entities, edges, communities."""
        entity_changes = self._entity_changes()
        relationship_changes = self._relationship_changes()
        community_changes = classify_communities(self._before, self._after)
        status = (
            PostGraphStatus.UNCHANGED
            if (
                all(c.change is EntityChangeType.UNCHANGED for c in entity_changes)
                and all(c.change is RelationshipChangeType.UNCHANGED for c in relationship_changes)
                and all(c.change is CommunityChangeType.PRESERVED for c in community_changes)
            )
            else PostGraphStatus.AVAILABLE
        )
        return GraphDiffResult(
            status=status,
            entity_changes=entity_changes,
            relationship_changes=relationship_changes,
            community_changes=community_changes,
        )

    def _entity_changes(self) -> tuple[EntityChange, ...]:
        before = {entity.name: entity for entity in self._before.entities}
        after = {entity.name: entity for entity in self._after.entities}
        changes: list[EntityChange] = []
        for entity_id in sorted(before.keys() | after.keys()):
            before_entity = before.get(entity_id)
            after_entity = after.get(entity_id)
            if before_entity is None and after_entity is not None:
                changes.append(EntityChange(
                    entity_id=entity_id, change=EntityChangeType.ADDED,
                    after=entity_attributes(after_entity)
                ))
            elif after_entity is None and before_entity is not None:
                changes.append(EntityChange(
                    entity_id=entity_id, change=EntityChangeType.REMOVED,
                    before=entity_attributes(before_entity)
                ))
            elif before_entity is not None and after_entity is not None:
                before_attrs = entity_attributes(before_entity)
                after_attrs = entity_attributes(after_entity)
                change = (
                    EntityChangeType.UNCHANGED
                    if before_attrs == after_attrs
                    else EntityChangeType.CHANGED
                )
                changes.append(EntityChange(
                    entity_id=entity_id,
                    change=change,
                    before=before_attrs,
                    after=after_attrs,
                ))
        return tuple(changes)

    def _relationship_changes(self) -> tuple[RelationshipChange, ...]:
        before = _relationship_map(self._before)
        after = _relationship_map(self._after)
        changes: list[RelationshipChange] = []
        for identity in sorted(before.keys() | after.keys(), key=_identity_key):
            before_attrs = before.get(identity)
            after_attrs = after.get(identity)
            if before_attrs is None and after_attrs is not None:
                changes.append(RelationshipChange(
                    identity=identity,
                    change=RelationshipChangeType.ADDED,
                    after=after_attrs,
                ))
            elif after_attrs is None and before_attrs is not None:
                changes.append(RelationshipChange(
                    identity=identity,
                    change=RelationshipChangeType.REMOVED,
                    before=before_attrs,
                ))
            elif before_attrs is not None and after_attrs is not None:
                change = (
                    RelationshipChangeType.UNCHANGED
                    if before_attrs == after_attrs
                    else RelationshipChangeType.CHANGED
                )
                changes.append(RelationshipChange(
                    identity=identity,
                    change=change,
                    before=before_attrs,
                    after=after_attrs,
                ))
        return tuple(changes)


def diff_graphs(before: GraphData | None, after: GraphData | None) -> GraphDiffResult:
    """Compute graph diff, returning typed missing/invalid states instead of raising."""
    if before is None:
        return GraphDiffResult(
            status=PostGraphStatus.MISSING,
            error_detail="pre-fix graph snapshot is missing",
        )
    if after is None:
        return GraphDiffResult(
            status=PostGraphStatus.MISSING,
            error_detail="post-fix graph snapshot is missing",
        )
    if not isinstance(before, GraphData) or not isinstance(after, GraphData):
        return GraphDiffResult(
            status=PostGraphStatus.INVALID,
            error_detail="pre-fix and post-fix graph snapshots must be GraphData objects",
        )
    try:
        return GraphDiffer(before, after).compute()
    except (TypeError, ValueError, AttributeError) as exc:
        return GraphDiffResult(status=PostGraphStatus.INVALID, error_detail=str(exc))


def _relationship_map(reader: GraphData) -> dict[RelationshipIdentity, dict[str, object]]:
    relationships = {}
    for relationship in reader.relationships:
        relationships[relationship_identity(relationship)] = relationship_attributes(relationship)
    return relationships


def _identity_key(identity: RelationshipIdentity) -> tuple[str, str, str, str]:
    return (identity.source_id, identity.target_id, identity.rel_type, identity.direction)
