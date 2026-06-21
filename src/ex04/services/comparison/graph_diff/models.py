"""Immutable graph-diff DTOs for T6.09."""

from __future__ import annotations

from dataclasses import asdict, dataclass, field
from enum import Enum
from pathlib import Path
from typing import Any


class PostGraphStatus(Enum):
    """Availability state for the post-fix graph snapshot."""

    AVAILABLE = "available"
    UNCHANGED = "unchanged"
    BLOCKED = "blocked"
    MISSING = "missing"
    INVALID = "invalid"


class EntityChangeType(Enum):
    """Entity-level diff classification."""

    ADDED = "added"
    REMOVED = "removed"
    CHANGED = "changed"
    UNCHANGED = "unchanged"


class RelationshipChangeType(Enum):
    """Relationship-level diff classification."""

    ADDED = "added"
    REMOVED = "removed"
    CHANGED = "changed"
    UNCHANGED = "unchanged"


class CommunityChangeType(Enum):
    """Community-level diff classification."""

    PRESERVED = "preserved"
    EXPANDED = "expanded"
    CONTRACTED = "contracted"
    SPLIT = "split"
    MERGED = "merged"
    ADDED = "added"
    REMOVED = "removed"


@dataclass(frozen=True, slots=True)
class RelationshipIdentity:
    """Stable relationship identity independent of non-identity attributes."""

    source_id: str
    target_id: str
    rel_type: str
    direction: str = "directed"


@dataclass(frozen=True, slots=True)
class EntityChange:
    """One entity classification."""

    entity_id: str
    change: EntityChangeType
    before: dict[str, Any] = field(default_factory=dict)
    after: dict[str, Any] = field(default_factory=dict)


@dataclass(frozen=True, slots=True)
class RelationshipChange:
    """One relationship classification."""

    identity: RelationshipIdentity
    change: RelationshipChangeType
    before: dict[str, Any] = field(default_factory=dict)
    after: dict[str, Any] = field(default_factory=dict)


@dataclass(frozen=True, slots=True)
class CommunityChange:
    """One community membership classification."""

    before_community: str | None
    after_community: str | None
    change: CommunityChangeType
    before_entities: tuple[str, ...] = ()
    after_entities: tuple[str, ...] = ()
    jaccard: float = 0.0


@dataclass(frozen=True, slots=True)
class GraphDiffResult:
    """Complete immutable graph-diff result."""

    status: PostGraphStatus
    entity_changes: tuple[EntityChange, ...] = ()
    relationship_changes: tuple[RelationshipChange, ...] = ()
    community_changes: tuple[CommunityChange, ...] = ()
    error_detail: str = ""

    def to_dict(self) -> dict[str, Any]:
        """Return canonical JSON-serializable data."""
        return _normalize(asdict(self))


@dataclass(frozen=True, slots=True)
class GraphDiffArtifacts:
    """Persisted graph-diff artifact paths and hashes."""

    json_path: Path
    markdown_path: Path
    graph_diff_hash: str
    markdown_hash: str


def _normalize(value: Any) -> Any:
    if isinstance(value, Enum):
        return value.value
    if isinstance(value, Path):
        return str(value)
    if isinstance(value, dict):
        return {k: _normalize(v) for k, v in value.items()}
    if isinstance(value, list | tuple):
        return [_normalize(v) for v in value]
    return value
