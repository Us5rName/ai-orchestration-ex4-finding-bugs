"""Core graph data types — entities, relationships, communities.

Re-exports all shared types for backward-compatible single-import usage.
T4.19a enrichment: Entity/Relationship carry stable IDs, display labels,
confidence state, anchors, and metadata. All existing call sites preserved.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from types import MappingProxyType
from typing import Any

from ex04.shared.types_graph_enums import ConfidenceState, EdgeDirection
from ex04.shared.types_metrics import (
    ComparisonMetrics,
    ComparisonReport,
    RunMetrics,
    TokenMetrics,
)
from ex04.shared.types_results import (
    InvestigationResult,
    PipelineResult,
    ProviderResponse,
    Suspect,
)

__all__ = [
    "Community",
    "ConfidenceState",
    "EdgeDirection",
    "Entity",
    "GraphData",
    "Relationship",
    "TokenMetrics",
    "RunMetrics",
    "ComparisonMetrics",
    "ComparisonReport",
    "ProviderResponse",
    "Suspect",
    "InvestigationResult",
    "PipelineResult",
]


@dataclass
class Entity:
    """Code entity (class, function, file, module) with enriched metadata.

    Fields `name`/`kind`/`file_path`/`line_range` are backward-compatible.
    New: `label` (display name separate from stable ID), `community`,
    `metadata`. Use `entity.id` as stable identity going forward.
    """

    name: str
    kind: str = ""
    file_path: str = ""
    line_range: tuple[int, int] = field(default_factory=lambda: (0, 0))
    label: str = ""
    community: int | None = None
    metadata: dict[str, Any] = field(default_factory=dict)

    @property
    def id(self) -> str:
        """Stable entity identity (alias for name)."""
        return self.name

    def immutable_metadata(self) -> MappingProxyType[str, Any]:
        """Return a read-only view of metadata."""
        return MappingProxyType(self.metadata)


@dataclass
class Relationship:
    """Directed relationship between two code entities with enriched metadata.

    Fields `source`/`target`/`type` are backward-compatible. New: `key`
    (unique edge identity for parallel edges), `confidence`/`confidence_score`/
    `weight`/`source_anchor`/`metadata`. Use property aliases for new code.
    Missing confidence resolves to UNKNOWN — never silently upgraded.
    """

    source: str
    target: str
    type: str = ""
    key: str = ""
    confidence: str | None = None
    confidence_score: float | None = None
    weight: float | None = None
    source_anchor: str | None = None
    metadata: dict[str, Any] = field(default_factory=dict)

    @property
    def source_id(self) -> str:
        """Stable source entity ID (alias for source)."""
        return self.source

    @property
    def target_id(self) -> str:
        """Stable target entity ID (alias for target)."""
        return self.target

    @property
    def rel_type(self) -> str:
        """Relationship type (alias for type)."""
        return self.type

    @property
    def confidence_state(self) -> ConfidenceState:
        """Resolved confidence; absent confidence → UNKNOWN."""
        if self.confidence is None:
            return ConfidenceState.UNKNOWN
        try:
            return ConfidenceState(self.confidence.lower())
        except ValueError:
            return ConfidenceState.UNKNOWN

    def immutable_metadata(self) -> MappingProxyType[str, Any]:
        """Return a read-only view of metadata."""
        return MappingProxyType(self.metadata)


@dataclass
class Community:
    """Detected community (cluster) of entities.

    Attributes:
        name: Community identifier.
        entities: Entity names in this community.
        size: Number of entities.
    """

    name: str
    entities: list[str] = field(default_factory=list)
    size: int = 0


@dataclass
class GraphData:
    """Structured graph data from Grphify output.

    Attributes:
        entities: All detected code entities.
        relationships: All relationships between entities.
        communities: Detected community clusters.
    """

    entities: list[Entity] = field(default_factory=list)
    relationships: list[Relationship] = field(default_factory=list)
    communities: list[Community] = field(default_factory=list)
