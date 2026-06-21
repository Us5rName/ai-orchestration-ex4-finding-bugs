"""Orphan Detector — finds isolated nodes and weakly connected components.

EXT-1 (FR-7.5): Walk graph entities with no or few incoming edges and report
disconnected modules. Low connectivity does not imply a defect; this report
is analytical only.

Traceability: [PRD-EXT §EXT-1], [TODO T7.07]
"""

from __future__ import annotations

from dataclasses import dataclass, field

from ex04.shared.graph_ops import connected_components, degree_map
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

        degree = degree_map(graph_data.relationships)

        orphans = [
            OrphanNode(
                name=entity.name,
                kind=entity.kind,
                file_path=entity.file_path,
                connection_count=conn,
                source_anchor=_source_anchor(entity.file_path, entity.line_range),
            )
            for entity in graph_data.entities
            if (conn := degree.get(entity.name, 0)) <= min_connections
        ]

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
        return [
            WeakComponent(component_id, members, len(members))
            for component_id, members in enumerate(
                connected_components(graph_data.entities, graph_data.relationships),
                start=1,
            )
            if len(members) <= self._WEAK_COMPONENT_MAX_SIZE
        ]


def _source_anchor(file_path: str, line_range: tuple[int, int]) -> str:
    if not file_path:
        return "unknown"
    return f"{file_path}:{line_range[0]}-{line_range[1]}"
