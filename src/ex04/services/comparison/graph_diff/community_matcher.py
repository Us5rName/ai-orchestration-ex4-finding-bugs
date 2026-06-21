"""Deterministic community matching by entity membership overlap."""

from __future__ import annotations

from dataclasses import dataclass

from ex04.services.comparison.graph_diff.models import CommunityChange, CommunityChangeType
from ex04.shared.types import GraphData


@dataclass(frozen=True, slots=True)
class CommunityMatch:
    """Best deterministic match from one pre community to one post community."""

    before_id: str
    after_id: str
    before_entities: tuple[str, ...]
    after_entities: tuple[str, ...]
    jaccard: float


def community_members(graph: GraphData) -> dict[str, tuple[str, ...]]:
    """Return non-empty communities keyed by their raw community ID string."""
    grouped: dict[str, list[str]] = {}
    for entity in graph.entities:
        community = entity.community
        if community is None:
            continue
        grouped.setdefault(str(community), []).append(entity.name)
    return {community: tuple(sorted(ids)) for community, ids in grouped.items() if ids}


def classify_communities(before: GraphData, after: GraphData) -> tuple[CommunityChange, ...]:
    """Classify community changes using overlap, not raw community IDs."""
    before_members = community_members(before)
    after_members = community_members(after)
    matched_before: set[str] = set()
    matched_after: set[str] = set()
    changes: list[CommunityChange] = []

    for before_id in sorted(before_members):
        candidates = _ranked_candidates(before_id, before_members, after_members)
        if not candidates:
            changes.append(_removed(before_id, before_members[before_id]))
            matched_before.add(before_id)
            continue
        overlaps = [
            after_id for after_id, score in candidates
            if score > 0 and _intersection(before_members[before_id], after_members[after_id])
        ]
        if len(overlaps) > 1:
            changes.append(CommunityChange(
                before_community=before_id,
                after_community=None,
                change=CommunityChangeType.SPLIT,
                before_entities=before_members[before_id],
                after_entities=tuple(sorted({e for aid in overlaps for e in after_members[aid]})),
                jaccard=max(score for _, score in candidates),
            ))
            matched_before.add(before_id)
            matched_after.update(overlaps)
            continue
        after_id, score = candidates[0]
        if score <= 0:
            changes.append(_removed(before_id, before_members[before_id]))
            matched_before.add(before_id)
            continue
        before_set = set(before_members[before_id])
        after_set = set(after_members[after_id])
        reverse_overlaps = [
            bid for bid, members in before_members.items()
            if _intersection(members, after_members[after_id])
        ]
        if len(reverse_overlaps) > 1:
            change = CommunityChangeType.MERGED
        elif before_set == after_set:
            change = CommunityChangeType.PRESERVED
        elif before_set < after_set:
            change = CommunityChangeType.EXPANDED
        elif after_set < before_set:
            change = CommunityChangeType.CONTRACTED
        else:
            change = CommunityChangeType.PRESERVED
        changes.append(CommunityChange(
            before_community=before_id,
            after_community=after_id,
            change=change,
            before_entities=before_members[before_id],
            after_entities=after_members[after_id],
            jaccard=score,
        ))
        matched_before.add(before_id)
        matched_after.add(after_id)

    for before_id in sorted(set(before_members) - matched_before):
        changes.append(_removed(before_id, before_members[before_id]))
    for after_id in sorted(set(after_members) - matched_after):
        changes.append(CommunityChange(
            before_community=None,
            after_community=after_id,
            change=CommunityChangeType.ADDED,
            after_entities=after_members[after_id],
        ))
    return tuple(sorted(
        changes,
        key=lambda c: (
            c.change.value,
            c.before_community or "",
            c.after_community or "",
            c.before_entities,
            c.after_entities,
        ),
    ))


def _ranked_candidates(
    before_id: str,
    before_members: dict[str, tuple[str, ...]],
    after_members: dict[str, tuple[str, ...]],
) -> list[tuple[str, float]]:
    before_set = set(before_members[before_id])
    ranked = [
        (after_id, _jaccard(before_set, set(after_entities)))
        for after_id, after_entities in after_members.items()
    ]
    return sorted(ranked, key=lambda item: (-item[1], item[0]))


def _jaccard(left: set[str], right: set[str]) -> float:
    if not left and not right:
        return 1.0
    union = left | right
    if not union:
        return 0.0
    return len(left & right) / len(union)


def _intersection(left: tuple[str, ...], right: tuple[str, ...]) -> set[str]:
    return set(left) & set(right)


def _removed(community_id: str, members: tuple[str, ...]) -> CommunityChange:
    return CommunityChange(
        before_community=community_id,
        after_community=None,
        change=CommunityChangeType.REMOVED,
        before_entities=members,
    )
