"""Immutable public query views and snapshot helpers for GraphReader.

Traceability: [TODO T4.19], [PLAN ADR-007].
"""

from __future__ import annotations

from dataclasses import dataclass
from types import MappingProxyType
from typing import Any


@dataclass(frozen=True, slots=True)
class EntityView:
    """Immutable snapshot of one graph entity.

    ``entity_id`` is the stable identity key; ``label`` is the display name.
    Duplicate labels with unique IDs are valid.
    """

    entity_id: str
    label: str
    kind: str
    file_path: str
    line_range: tuple[int, int]
    community: int | None
    metadata: MappingProxyType[str, Any]

    @property
    def id(self) -> str:
        """Stable entity identity."""
        return self.entity_id

    @property
    def name(self) -> str:
        """Backward-compat alias for entity_id."""
        return self.entity_id


@dataclass(frozen=True, slots=True)
class RelationshipView:
    """Immutable snapshot of one directed relationship.

    ``key`` is the canonical stable discriminator. Direction, parallel
    edges, and type are all preserved.
    """

    key: str
    source_id: str
    target_id: str
    rel_type: str
    confidence: str | None
    confidence_score: float | None
    weight: float | None
    source_anchor: str | None
    metadata: MappingProxyType[str, Any]

    @property
    def source(self) -> str:
        """Backward-compat alias for source_id."""
        return self.source_id

    @property
    def target(self) -> str:
        """Backward-compat alias for target_id."""
        return self.target_id

    @property
    def type(self) -> str:
        """Backward-compat alias for rel_type."""
        return self.rel_type


@dataclass(frozen=True, slots=True)
class DegreeEntry:
    """One entry in the degree ranking: entity view + incident count."""

    entity: EntityView
    degree: int


def to_entity_view(entity: object) -> EntityView:
    """Convert any Entity-like to an immutable EntityView snapshot."""
    eid = str(getattr(entity, "name", "") or "")
    lbl = str(getattr(entity, "label", "") or eid)
    return EntityView(
        entity_id=eid,
        label=lbl,
        kind=str(getattr(entity, "kind", "")),
        file_path=str(getattr(entity, "file_path", "")),
        line_range=tuple(getattr(entity, "line_range", (0, 0))),  # type: ignore[arg-type]
        community=getattr(entity, "community", None),
        metadata=MappingProxyType(dict(getattr(entity, "metadata", {}) or {})),
    )


def to_rel_view(rel: object) -> RelationshipView:
    """Convert any Relationship-like to an immutable RelationshipView snapshot."""
    return RelationshipView(
        key=str(getattr(rel, "key", "") or ""),
        source_id=str(getattr(rel, "source", "") or ""),
        target_id=str(getattr(rel, "target", "") or ""),
        rel_type=str(getattr(rel, "type", "") or ""),
        confidence=getattr(rel, "confidence", None),
        confidence_score=getattr(rel, "confidence_score", None),
        weight=getattr(rel, "weight", None),
        source_anchor=getattr(rel, "source_anchor", None),
        metadata=MappingProxyType(dict(getattr(rel, "metadata", {}) or {})),
    )
