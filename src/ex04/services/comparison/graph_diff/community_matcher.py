"""Deterministic thresholded community matching."""

from __future__ import annotations

from dataclasses import dataclass

from ex04.services.comparison.graph_diff.community_components import overlap_components
from ex04.services.comparison.graph_diff.models import CommunityChange, CommunityChangeType
from ex04.services.graph.interface import GraphReaderInterface


@dataclass(frozen=True, slots=True)
class CommunityMatchingConfig:
    jaccard_threshold: float = 0.5

    def __post_init__(self) -> None:
        if not 0.0 <= self.jaccard_threshold <= 1.0:
            raise ValueError("jaccard_threshold must be in [0, 1]")


def community_members(reader: GraphReaderInterface) -> dict[str, tuple[str, ...]]:
    grouped: dict[str, tuple[str, ...]] = {}
    for community, nodes in reader.communities().items():
        if community is None:
            continue
        members = tuple(node.entity_id for node in nodes)
        if members:
            grouped[str(community)] = members
    return grouped


def classify_communities(
    before: GraphReaderInterface,
    after: GraphReaderInterface,
    config: CommunityMatchingConfig | None = None,
) -> tuple[CommunityChange, ...]:
    cfg = config or CommunityMatchingConfig()
    before_members = community_members(before)
    after_members = community_members(after)
    exact = _exact_matches(before_members, after_members)
    used_before = {pair[0] for pair in exact}
    used_after = {pair[1] for pair in exact}
    changes = [
        _change(bid, aid, CommunityChangeType.PRESERVED, before_members, after_members, 1.0)
        for bid, aid in exact
    ]
    edges = _qualifying_edges(before_members, after_members, used_before, used_after, cfg)
    for before_ids, after_ids in overlap_components(edges):
        change_type = _classify_component(before_ids, after_ids, before_members, after_members)
        score = max(_jaccard(set(before_members[b]), set(after_members[a])) for b in before_ids for a in after_ids)
        changes.append(CommunityChange(
            before_community=",".join(before_ids) if before_ids else None,
            after_community=",".join(after_ids) if after_ids else None,
            change=change_type,
            before_entities=tuple(sorted({e for bid in before_ids for e in before_members[bid]})),
            after_entities=tuple(sorted({e for aid in after_ids for e in after_members[aid]})),
            jaccard=score,
        ))
        used_before.update(before_ids)
        used_after.update(after_ids)
    for bid in sorted(set(before_members) - used_before):
        changes.append(_change(bid, None, CommunityChangeType.REMOVED, before_members, after_members, 0.0))
    for aid in sorted(set(after_members) - used_after):
        changes.append(_change(None, aid, CommunityChangeType.ADDED, before_members, after_members, 0.0))
    return tuple(sorted(changes, key=_sort_key))


def _exact_matches(
    before: dict[str, tuple[str, ...]],
    after: dict[str, tuple[str, ...]],
) -> tuple[tuple[str, str], ...]:
    matches = []
    remaining_after = set(after)
    for bid in sorted(before):
        for aid in sorted(remaining_after):
            if before[bid] == after[aid]:
                matches.append((bid, aid))
                remaining_after.remove(aid)
                break
    return tuple(matches)


def _qualifying_edges(
    before: dict[str, tuple[str, ...]],
    after: dict[str, tuple[str, ...]],
    used_before: set[str],
    used_after: set[str],
    config: CommunityMatchingConfig,
) -> dict[str, set[str]]:
    edges: dict[str, set[str]] = {}
    for bid, before_entities in before.items():
        if bid in used_before:
            continue
        for aid, after_entities in after.items():
            if aid in used_after:
                continue
            if _jaccard(set(before_entities), set(after_entities)) >= config.jaccard_threshold:
                edges.setdefault(f"b:{bid}", set()).add(f"a:{aid}")
                edges.setdefault(f"a:{aid}", set()).add(f"b:{bid}")
    return edges


def _classify_component(
    before_ids: tuple[str, ...],
    after_ids: tuple[str, ...],
    before: dict[str, tuple[str, ...]],
    after: dict[str, tuple[str, ...]],
) -> CommunityChangeType:
    if len(before_ids) > 1 and len(after_ids) == 1:
        return CommunityChangeType.MERGED
    if len(before_ids) == 1 and len(after_ids) > 1:
        return CommunityChangeType.SPLIT
    before_set = set(before[before_ids[0]])
    after_set = set(after[after_ids[0]])
    if before_set < after_set:
        return CommunityChangeType.EXPANDED
    if after_set < before_set:
        return CommunityChangeType.CONTRACTED
    if before_set == after_set:
        return CommunityChangeType.PRESERVED
    return CommunityChangeType.REORGANIZED


def _change(
    bid: str | None,
    aid: str | None,
    change: CommunityChangeType,
    before: dict[str, tuple[str, ...]],
    after: dict[str, tuple[str, ...]],
    score: float,
) -> CommunityChange:
    return CommunityChange(bid, aid, change, before.get(bid or "", ()), after.get(aid or "", ()), score)


def _jaccard(left: set[str], right: set[str]) -> float:
    union = left | right
    return len(left & right) / len(union) if union else 0.0


def _sort_key(change: CommunityChange) -> tuple[str, str, str, tuple[str, ...], tuple[str, ...]]:
    return (
        change.change.value,
        change.before_community or "",
        change.after_community or "",
        change.before_entities,
        change.after_entities,
    )
