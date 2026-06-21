"""GraphReader — typed read-only query facade over GraphData.

Provides O(1)-indexed access to entities, directed edges, degree rankings,
and community membership. Indexes are built at construction; no per-call
graph scanning. Traceability: [TODO T4.19], [PLAN ADR-007].
"""

from __future__ import annotations

from collections import defaultdict
from pathlib import Path
from types import MappingProxyType
from typing import TYPE_CHECKING

from ex04.shared.types import EdgeDirection, Entity, GraphData, Relationship

if TYPE_CHECKING:
    from collections.abc import Mapping


class GraphReader:
    """Canonical typed read-only query facade over GraphData.

    Accepts existing GraphData or delegates parsing to GraphParser via
    ``from_path()``. Maintains constructor-time indexes. Never creates
    a second raw-JSON parsing path.
    """

    def __init__(self, graph_data: GraphData) -> None:
        """Build indexes from parsed GraphData."""
        self._data = graph_data
        self._entity_by_id: dict[str, Entity] = {}
        self._outgoing: dict[str, list[Relationship]] = defaultdict(list)
        self._incoming: dict[str, list[Relationship]] = defaultdict(list)
        self._incident: dict[str, list[Relationship]] = defaultdict(list)
        self._degree: dict[str, int] = defaultdict(int)
        self._communities: dict[str | None, list[Entity]] = defaultdict(list)
        self._build_indexes()

    def _build_indexes(self) -> None:
        """Populate all internal indexes from graph data."""
        for entity in self._data.entities:
            self._entity_by_id[entity.id] = entity
            key: str | None = (
                str(entity.community) if entity.community is not None else None
            )
            self._communities[key].append(entity)
        for rel in self._data.relationships:
            src, tgt = rel.source_id, rel.target_id
            self._outgoing[src].append(rel)
            self._incoming[tgt].append(rel)
            self._incident[src].append(rel)
            if src != tgt:
                self._incident[tgt].append(rel)
            self._degree[src] += 1
            self._degree[tgt] += 1

    @classmethod
    def from_path(cls, graph_path: Path, parser: object = None) -> GraphReader:
        """Construct by parsing a graph.json file via GraphParser.

        Args:
            graph_path: Path to a Grphify graph.json artifact.
            parser: Optional GraphParser instance; a new one is created if None.
        """
        from ex04.services.graph.parser import GraphParser  # avoid top-level circular

        p = parser if isinstance(parser, GraphParser) else GraphParser()
        return cls(p.parse(graph_path))

    def node(self, node_id: str) -> Entity | None:
        """Return entity with the given stable ID, or None if unknown."""
        return self._entity_by_id.get(node_id)

    def all_nodes(self) -> tuple[Entity, ...]:
        """Return all entities sorted deterministically by stable ID."""
        return tuple(sorted(self._entity_by_id.values(), key=lambda e: e.id))

    def edges_of(
        self,
        node_id: str,
        *,
        direction: EdgeDirection = EdgeDirection.BOTH,
    ) -> tuple[Relationship, ...]:
        """Return edges for node_id filtered by direction.

        Returns empty tuple for unknown node IDs. Parallel relationships
        and direction are preserved.
        """
        if direction is EdgeDirection.OUTGOING:
            rels = self._outgoing.get(node_id, [])
        elif direction is EdgeDirection.INCOMING:
            rels = self._incoming.get(node_id, [])
        else:
            rels = self._incident.get(node_id, [])
        return tuple(sorted(rels, key=lambda r: r.key))

    def top_n_by_degree(self, n: int) -> tuple[tuple[Entity, int], ...]:
        """Return up to n entities ranked by incident degree descending.

        Tie-breaking: degree desc, then entity ID asc (deterministic).
        n < 0 raises ValueError. n == 0 returns empty. n > size returns all.
        """
        if n < 0:
            raise ValueError(f"n must be >= 0, got {n!r}.")
        if n == 0:
            return ()
        ranked = sorted(
            self._entity_by_id.values(),
            key=lambda e: (-self._degree.get(e.id, 0), e.id),
        )
        return tuple(
            (entity, self._degree.get(entity.id, 0)) for entity in ranked[:n]
        )

    def communities(self) -> Mapping[str | None, tuple[Entity, ...]]:
        """Return entities grouped by community key (str ID or None).

        Key is the string form of the community integer, or None for
        unassigned entities. Results are immutable and deterministically
        ordered within each community.
        """
        return MappingProxyType(
            {
                key: tuple(sorted(members, key=lambda e: e.id))
                for key, members in self._communities.items()
            }
        )
