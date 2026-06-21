"""Community overlap component helpers."""

from __future__ import annotations


def overlap_components(
    edges: dict[str, set[str]],
) -> tuple[tuple[tuple[str, ...], tuple[str, ...]], ...]:
    """Return deterministic connected components from a bipartite overlap graph."""
    seen: set[str] = set()
    components = []
    for start in sorted(edges):
        if start in seen:
            continue
        nodes = _walk_component(start, edges, seen)
        components.append((
            tuple(sorted(node[2:] for node in nodes if node.startswith("b:"))),
            tuple(sorted(node[2:] for node in nodes if node.startswith("a:"))),
        ))
    return tuple(components)


def _walk_component(start: str, edges: dict[str, set[str]], seen: set[str]) -> set[str]:
    stack = [start]
    nodes: set[str] = set()
    while stack:
        node = stack.pop()
        if node in seen:
            continue
        seen.add(node)
        nodes.add(node)
        stack.extend(sorted(edges.get(node, set()) - seen, reverse=True))
    return nodes
