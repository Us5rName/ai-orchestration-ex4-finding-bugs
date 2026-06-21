"""GraphReader — typed read-only query facade over GraphData.

Provides O(1)-indexed access to entities, directed edges, degree rankings,
and community membership. Indexes are built at construction from a deep
snapshot — mutating the original GraphData cannot change reader results.
All public methods return frozen EntityView / RelationshipView objects.

Traceability: [TODO T4.19], [PLAN ADR-007].
"""

from __future__ import annotations

from collections import defaultdict
from pathlib import Path
from types import MappingProxyType
from typing import TYPE_CHECKING, Protocol, runtime_checkable  # noqa: F401

from ex04.services.graph.reader_models import (
    EntityView,
    RelationshipView,
    to_entity_view,
    to_rel_view,
)
from ex04.shared.types import EdgeDirection, GraphData

if TYPE_CHECKING:
    from collections.abc import Mapping


@runtime_checkable
class GraphDataParser(Protocol):
    """Narrow protocol for parser injection into GraphReader.from_path()."""

    def parse(self, graph_path: Path) -> GraphData:
        """Parse a graph artifact file into GraphData."""
        ...


class GraphReader:
    """Canonical typed read-only query facade over GraphData.

    Snapshots input at construction. Mutating the original GraphData,
    Entity, or Relationship objects cannot change reader results.
    All returned objects are immutable EntityView / RelationshipView instances.
    Never creates a second raw-JSON parsing path.
    """

    def __init__(self, graph_data: GraphData) -> None:
        """Build indexes from a deep snapshot of GraphData."""
        self._entity_by_id: dict[str, EntityView] = {}
        self._outgoing: dict[str, list[RelationshipView]] = defaultdict(list)
        self._incoming: dict[str, list[RelationshipView]] = defaultdict(list)
        self._incident: dict[str, list[RelationshipView]] = defaultdict(list)
        self._degree: dict[str, int] = defaultdict(int)
        self._communities: dict[str | None, list[EntityView]] = defaultdict(list)
        self._build_indexes(graph_data)

    def _build_indexes(self, graph_data: GraphData) -> None:
        """Snapshot and index entities and relationships."""
        for entity in graph_data.entities:
            ev = to_entity_view(entity)
            self._entity_by_id[ev.entity_id] = ev
            key: str | None = str(ev.community) if ev.community is not None else None
            self._communities[key].append(ev)
        for rel in graph_data.relationships:
            rv = to_rel_view(rel)
            src, tgt = rv.source_id, rv.target_id
            self._outgoing[src].append(rv)
            self._incoming[tgt].append(rv)
            self._incident[src].append(rv)
            if src != tgt:
                self._incident[tgt].append(rv)
            self._degree[src] += 1
            self._degree[tgt] += 1

    @classmethod
    def from_path(cls, graph_path: Path, parser: object = None) -> GraphReader:
        """Construct by parsing a graph.json file via an injected parser.

        Args:
            graph_path: Path to a Grphify graph.json artifact.
            parser: Any object satisfying GraphDataParser protocol.
                    A new GraphParser is created if None or incompatible.
        """
        from ex04.services.graph.parser import GraphParser  # avoid top-level circular

        resolved: GraphDataParser
        if parser is not None and isinstance(parser, GraphDataParser):
            resolved = parser  # type: ignore[assignment]
        else:
            resolved = GraphParser()
        return cls(resolved.parse(graph_path))

    def node(self, node_id: str) -> EntityView | None:
        """Return immutable EntityView with given stable ID, or None."""
        return self._entity_by_id.get(node_id)

    def all_nodes(self) -> tuple[EntityView, ...]:
        """Return all entities sorted deterministically by stable ID."""
        return tuple(sorted(self._entity_by_id.values(), key=lambda e: e.entity_id))

    def edges_of(
        self,
        node_id: str,
        *,
        direction: EdgeDirection = EdgeDirection.BOTH,
    ) -> tuple[RelationshipView, ...]:
        """Return immutable RelationshipViews for node_id filtered by direction.

        Returns empty tuple for unknown node IDs. Parallel relationships and
        direction are preserved exactly.
        """
        if direction is EdgeDirection.OUTGOING:
            rels = self._outgoing.get(node_id, [])
        elif direction is EdgeDirection.INCOMING:
            rels = self._incoming.get(node_id, [])
        else:
            rels = self._incident.get(node_id, [])
        return tuple(sorted(rels, key=lambda r: r.key))

    def top_n_by_degree(self, n: int) -> tuple[tuple[EntityView, int], ...]:
        """Return up to n entities ranked by incident degree descending.

        Tie-breaking: degree desc, then entity_id asc (deterministic).
        Raises ValueError if n < 0.
        """
        if n < 0:
            raise ValueError(f"n must be >= 0, got {n!r}.")
        if n == 0:
            return ()
        ranked = sorted(
            self._entity_by_id.values(),
            key=lambda e: (-self._degree.get(e.entity_id, 0), e.entity_id),
        )
        return tuple(
            (entity, self._degree.get(entity.entity_id, 0)) for entity in ranked[:n]
        )

    def communities(self) -> Mapping[str | None, tuple[EntityView, ...]]:
        """Return entities by community key (str form or None); read-only."""
        return MappingProxyType(
            {k: tuple(sorted(v, key=lambda e: e.entity_id)) for k, v in self._communities.items()}
        )
