"""BFS traversal helpers for PatchImpactAnalyzer.

Extracted to keep patch_impact.py within the 150-line limit.
"""

from __future__ import annotations

from collections.abc import Mapping, Sequence

from ex04.services.analysis.patch_impact_types import ImpactedNode
from ex04.shared.types import Entity, Relationship


def build_reverse_edges(relationships: Sequence[Relationship]) -> dict[str, list[str]]:
    """Build reverse-dependency map: target -> list of sources."""
    rev: dict[str, list[str]] = {}
    for rel in relationships:
        rev.setdefault(rel.target, []).append(rel.source)
    return rev


def bfs_impact(
    start: str,
    rev: dict[str, list[str]],
    entity_map: Mapping[str, Entity],
    max_depth: int,
    direct: list[ImpactedNode],
    transitive: list[ImpactedNode],
    all_paths: list[list[str]],
) -> None:
    """BFS from start through reverse edges, collecting impact nodes."""
    visited = {start}
    queue: list[tuple[str, int, list[str]]] = [(start, 0, [start])]
    while queue:
        node, depth, path = queue.pop(0)
        for dependent in rev.get(node, []):
            if dependent in visited:
                continue
            if depth + 1 > max_depth:
                continue
            visited.add(dependent)
            new_path = path + [dependent]
            entity = entity_map.get(dependent)
            if isinstance(entity, Entity):
                anchor = (
                    f"{entity.file_path}:{entity.line_range[0]}"
                    if entity.file_path
                    else "unknown"
                )
                impacted = ImpactedNode(
                    name=dependent,
                    kind=entity.kind,
                    file_path=entity.file_path,
                    depth=depth + 1,
                    path_from_changed=new_path,
                    source_anchor=anchor,
                )
            else:
                impacted = ImpactedNode(
                    name=dependent,
                    kind="unknown",
                    file_path="",
                    depth=depth + 1,
                    path_from_changed=new_path,
                )
            if depth + 1 == 1:
                direct.append(impacted)
            else:
                transitive.append(impacted)
            all_paths.append(new_path)
            if depth + 1 < max_depth:
                queue.append((dependent, depth + 1, new_path))
