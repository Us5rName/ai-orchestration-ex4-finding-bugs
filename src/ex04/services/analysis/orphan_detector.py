"""Orphan Detector — finds isolated nodes and weakly connected components.

EXT-1 (FR-7.5): Walk graph entities with no or few incoming edges and report
disconnected modules. Low connectivity does not imply a defect; this report
is analytical only.

Traceability: [PRD-EXT §EXT-1], [TODO T7.07]
"""

from __future__ import annotations

from dataclasses import dataclass, field

from ex04.shared.types import GraphData


@dataclass
class OrphanNode:
    """An entity with connection count at or below the configured threshold."""

    name: str
    kind: str
    file_path: str
    connection_count: int
    source_anchor: str


@dataclass
class WeakComponent:
    """A small connected component below the weak-component size threshold."""

    component_id: int
    members: list[str] = field(default_factory=list)
    size: int = 0


@dataclass
class OrphanReport:
    """Report of isolated and weakly connected entities in the graph."""

    orphan_nodes: list[OrphanNode] = field(default_factory=list)
    weak_components: list[WeakComponent] = field(default_factory=list)
    total_entities: int = 0
    orphan_count: int = 0
    weak_component_count: int = 0
    threshold_used: int = 0
    limitations: list[str] = field(default_factory=list)
    evidence_class: str = "deterministic_keyless_evidence"


class OrphanDetector:
    """Detect orphan nodes and weakly connected components in a graph.

    Uses degree-based threshold for orphan detection and BFS for
    connected-component enumeration. Findings are informational only —
    low connectivity does not automatically indicate a defect.
    """

    _WEAK_COMPONENT_MAX_SIZE = 2

    def detect(self, graph_data: GraphData, min_connections: int = 0) -> OrphanReport:
        """Return OrphanReport for the given graph.

        Args:
            graph_data: Parsed Graphify output.
            min_connections: Nodes with <= this degree are orphan candidates.

        Returns:
            OrphanReport with orphan nodes, weak components, and limitations.
        """
        if not graph_data.entities and not graph_data.relationships:
            return OrphanReport(
                limitations=["Graph is empty — no entities or relationships."],
                threshold_used=min_connections,
            )

        degree: dict[str, int] = {}
        for rel in graph_data.relationships:
            degree[rel.source] = degree.get(rel.source, 0) + 1
            degree[rel.target] = degree.get(rel.target, 0) + 1

        orphans: list[OrphanNode] = []
        for entity in graph_data.entities:
            conn = degree.get(entity.name, 0)
            if conn <= min_connections:
                anchor = (
                    f"{entity.file_path}:{entity.line_range[0]}-{entity.line_range[1]}"
                    if entity.file_path
                    else "unknown"
                )
                orphans.append(
                    OrphanNode(
                        name=entity.name,
                        kind=entity.kind,
                        file_path=entity.file_path,
                        connection_count=conn,
                        source_anchor=anchor,
                    )
                )

        weak = self._find_weak_components(graph_data)
        report = OrphanReport(
            orphan_nodes=orphans,
            weak_components=weak,
            total_entities=len(graph_data.entities),
            orphan_count=len(orphans),
            weak_component_count=len(weak),
            threshold_used=min_connections,
            limitations=[
                "Low connectivity does not imply a defect.",
                "Connected-component algorithm uses undirected BFS.",
            ],
        )
        return report

    def _find_weak_components(self, graph_data: GraphData) -> list[WeakComponent]:
        """BFS connected-component detection (undirected)."""
        adjacency: dict[str, set[str]] = {}
        all_nodes = {e.name for e in graph_data.entities}
        for rel in graph_data.relationships:
            adjacency.setdefault(rel.source, set()).add(rel.target)
            adjacency.setdefault(rel.target, set()).add(rel.source)
            all_nodes.update([rel.source, rel.target])

        visited: set[str] = set()
        components: list[WeakComponent] = []
        cid = 0
        for node in sorted(all_nodes):
            if node in visited:
                continue
            cid += 1
            members: list[str] = []
            queue = [node]
            while queue:
                cur = queue.pop(0)
                if cur in visited:
                    continue
                visited.add(cur)
                members.append(cur)
                for nb in sorted(adjacency.get(cur, set())):
                    if nb not in visited:
                        queue.append(nb)
            if len(members) <= self._WEAK_COMPONENT_MAX_SIZE:
                components.append(WeakComponent(cid, members, len(members)))
        return components
