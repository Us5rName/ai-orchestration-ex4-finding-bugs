"""Graph Service Interface — contract for graph operations.

Defines the abstract base class that all graph service implementations
must follow. Enables parallel development — other modules depend only
on this interface, not on concrete implementations.

See ADR-005 for rationale.

Implementation: Phase 4 (T4.01–T4.03)
  - T4.01: GraphRunner (runner.py)
  - T4.02: GraphParser (parser.py)
  - T4.03: GraphAnalyzer (analyzer.py)
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from collections.abc import Mapping
from pathlib import Path
from types import MappingProxyType
from typing import Any, Protocol, cast

from ex04.shared.types import GraphData
from ex04.shared.types_graph_enums import EdgeDirection


class EntityGraphView(Protocol):
    """Read-only entity view protocol exposed across service boundaries."""

    entity_id: str
    label: str
    kind: str
    file_path: str
    line_range: tuple[int, int]
    community: int | None
    metadata: MappingProxyType[str, Any]


class RelationshipGraphView(Protocol):
    """Read-only relationship view protocol exposed across service boundaries."""

    key: str
    source_id: str
    target_id: str
    rel_type: str
    confidence: str | None
    confidence_score: float | None
    weight: float | None
    source_anchor: str | None
    metadata: MappingProxyType[str, Any]


class GraphReaderInterface(Protocol):
    """Typed read-only graph query boundary."""

    def all_nodes(self) -> tuple[EntityGraphView, ...]:
        """Return all graph entities in stable order."""
        ...

    def edges_of(
        self,
        node_id: str,
        *,
        direction: EdgeDirection = EdgeDirection.BOTH,
    ) -> tuple[RelationshipGraphView, ...]:
        """Return relationships for one entity."""
        ...

    def top_n_by_degree(self, n: int) -> tuple[tuple[EntityGraphView, int], ...]:
        """Return entities ranked by incident degree."""
        ...

    def communities(self) -> Mapping[str | None, tuple[EntityGraphView, ...]]:
        """Return community membership by community key."""
        ...


def build_graph_reader(graph_data: GraphData) -> GraphReaderInterface:
    """Construct the canonical GraphReader behind the graph service boundary."""
    from ex04.services.graph.reader import GraphReader

    return cast(GraphReaderInterface, GraphReader(graph_data))


class GraphServiceInterface(ABC):
    """Abstract interface for graph service operations.

    All graph-related operations (execution, parsing, analysis) must
    implement this interface. This enables dependency injection and
    mock-based testing.
    """

    @abstractmethod
    def extract(self, target_path: str) -> Path:
        """Extract code graph from target codebase.

        Args:
            target_path: Path to the target codebase directory.

        Returns:
            Path to the generated graph.json output file.
        """

    @abstractmethod
    def parse(self, graph_path: Path) -> GraphData:
        """Parse graph output into structured data.

        Args:
            graph_path: Path to the graph.json file.

        Returns:
            Structured GraphData with entities, relationships, communities.
        """

    @abstractmethod
    def analyze(self, graph_data: GraphData) -> dict[str, list]:
        """Analyze graph structure for insights.

        Args:
            graph_data: Parsed graph data to analyze.

        Returns:
            Dict with keys 'god_nodes', 'centrality_ranking', 'communities'.
        """
