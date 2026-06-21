"""Parallel relationship matching for graph diff."""

from __future__ import annotations

from collections import defaultdict
from dataclasses import dataclass

from ex04.services.comparison.graph_diff.canonicalize import field_changes, relationship_attributes
from ex04.services.comparison.graph_diff.models import (
    FrozenObject,
    RelationshipChange,
    RelationshipChangeType,
    RelationshipIdentity,
)
from ex04.services.graph.interface import GraphReaderInterface, RelationshipGraphView
from ex04.shared.types_graph_enums import EdgeDirection


@dataclass(frozen=True, slots=True)
class RelItem:
    identity: RelationshipIdentity
    attrs: FrozenObject


def relationship_changes(reader_before: GraphReaderInterface, reader_after: GraphReaderInterface) -> tuple[RelationshipChange, ...]:
    changes = []
    before_groups = relationship_groups(reader_before)
    after_groups = relationship_groups(reader_after)
    for key in sorted(before_groups.keys() | after_groups.keys()):
        changes.extend(match_group(before_groups.get(key, ()), after_groups.get(key, ())))
    return tuple(sorted(changes, key=relationship_change_key))


def relationship_groups(reader: GraphReaderInterface) -> dict[tuple[str, str, str, str], tuple[RelItem, ...]]:
    groups: dict[tuple[str, str, str, str], list[RelItem]] = defaultdict(list)
    for node in reader.all_nodes():
        for rel in reader.edges_of(node.entity_id, direction=EdgeDirection.OUTGOING):
            identity = identity_for(rel, rel.key)
            groups[(rel.source_id, rel.target_id, rel.rel_type, "directed")].append(
                RelItem(identity, relationship_attributes(rel))
            )
    return {key: tuple(sorted(value, key=rel_item_key)) for key, value in groups.items()}


def match_group(before: tuple[RelItem, ...], after: tuple[RelItem, ...]) -> list[RelationshipChange]:
    changes: list[RelationshipChange] = []
    remaining_before = list(before)
    remaining_after = list(after)
    _match_keyed(changes, remaining_before, remaining_after)
    _match_exact(changes, remaining_before, remaining_after)
    while remaining_before and remaining_after:
        left, right = min(
            ((left, right) for left in remaining_before for right in remaining_after),
            key=lambda pair: (
                len(field_changes(pair[0].attrs, pair[1].attrs)),
                rel_item_key(pair[0]),
                rel_item_key(pair[1]),
            ),
        )
        remaining_before.remove(left)
        remaining_after.remove(right)
        changes.append(relationship_change(left, right))
    changes.extend(RelationshipChange(item.identity, RelationshipChangeType.REMOVED, before=item.attrs) for item in remaining_before)
    changes.extend(RelationshipChange(item.identity, RelationshipChangeType.ADDED, after=item.attrs) for item in remaining_after)
    return changes


def _match_keyed(changes: list[RelationshipChange], before: list[RelItem], after: list[RelItem]) -> None:
    for left in tuple(before):
        match = next((right for right in after if left.identity.parallel_key and right.identity.parallel_key == left.identity.parallel_key), None)
        if match is not None:
            before.remove(left)
            after.remove(match)
            changes.append(relationship_change(left, match))


def _match_exact(changes: list[RelationshipChange], before: list[RelItem], after: list[RelItem]) -> None:
    for left in tuple(before):
        match = next((right for right in after if right.attrs == left.attrs), None)
        if match is not None:
            before.remove(left)
            after.remove(match)
            changes.append(relationship_change(left, match))


def relationship_change(before: RelItem, after: RelItem) -> RelationshipChange:
    changes = field_changes(before.attrs, after.attrs)
    change = RelationshipChangeType.UNCHANGED if not changes else RelationshipChangeType.CHANGED
    identity = before.identity if before.identity.parallel_key else after.identity
    return RelationshipChange(identity, change, before.attrs, after.attrs, changes)


def identity_for(rel: RelationshipGraphView, key: str) -> RelationshipIdentity:
    return RelationshipIdentity(rel.source_id, rel.target_id, rel.rel_type, "directed", key)


def rel_item_key(item: RelItem) -> tuple[str, str, str, str, str]:
    ident = item.identity
    return (ident.source_id, ident.target_id, ident.rel_type, ident.parallel_key, repr(item.attrs))


def relationship_change_key(change: RelationshipChange) -> tuple[str, str, str, str, str]:
    ident = change.identity
    return (ident.source_id, ident.target_id, ident.rel_type, ident.parallel_key, change.change.value)
