"""Core graph data types — entities, relationships, communities.

Defines the fundamental graph structures used by the Graph Service
and consumed by other services via the contract interfaces.

Re-exports all shared types from sub-modules for backward-compatible
single-import usage (e.g. `from ex04.shared.types import TokenMetrics`).
"""

from __future__ import annotations

from dataclasses import dataclass, field

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
    """Represents a code entity (class, function, file, module).

    Attributes:
        name: Entity name.
        kind: Entity type ('class', 'function', 'file', 'module').
        file_path: Source file path.
        line_range: (start_line, end_line) tuple.
    """

    name: str
    kind: str
    file_path: str = ""
    line_range: tuple[int, int] = field(default_factory=lambda: (0, 0))


@dataclass
class Relationship:
    """Represents a relationship between two code entities.

    Attributes:
        source: Source entity name.
        target: Target entity name.
        type: Relationship type (e.g. 'calls', 'inherits', 'imports').
    """

    source: str
    target: str
    type: str = ""


@dataclass
class Community:
    """Represents a detected community (cluster) of entities.

    Attributes:
        name: Community identifier.
        entities: List of entity names in this community.
        size: Number of entities in the community.
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
