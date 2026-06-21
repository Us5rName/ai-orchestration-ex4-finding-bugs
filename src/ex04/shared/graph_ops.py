"""Shared graph operations over parsed GraphData objects."""

from __future__ import annotations

from collections import defaultdict, deque
from collections.abc import Iterable

from ex04.shared.types import Entity, Relationship


def degree_map(relationships: Iterable[Relationship]) -> dict[str, int]:
    """Return undirected degree counts keyed by node name."""
    degree: dict[str, int] = defaultdict(int)
    for rel in relationships:
        degree[rel.source] += 1
        degree[rel.target] += 1
    return dict(degree)


def connected_components(
    entities: Iterable[Entity],
    relationships: Iterable[Relationship],
) -> list[list[str]]:
    """Return sorted undirected connected components."""
    adjacency, all_nodes = _adjacency(entities, relationships)
    visited: set[str] = set()
    components: list[list[str]] = []

    for node in sorted(all_nodes):
        if node in visited:
            continue
        members = _component_members(node, adjacency, visited)
        components.append(members)
    return components


def _adjacency(
    entities: Iterable[Entity],
    relationships: Iterable[Relationship],
) -> tuple[dict[str, set[str]], set[str]]:
    adjacency: dict[str, set[str]] = defaultdict(set)
    all_nodes = {entity.name for entity in entities}
    for rel in relationships:
        adjacency[rel.source].add(rel.target)
        adjacency[rel.target].add(rel.source)
        all_nodes.update((rel.source, rel.target))
    return dict(adjacency), all_nodes


def _component_members(
    start: str,
    adjacency: dict[str, set[str]],
    visited: set[str],
) -> list[str]:
    members: list[str] = []
    queue: deque[str] = deque([start])
    while queue:
        current = queue.popleft()
        if current in visited:
            continue
        visited.add(current)
        members.append(current)
        queue.extend(
            neighbor
            for neighbor in sorted(adjacency.get(current, set()))
            if neighbor not in visited
        )
    return members
