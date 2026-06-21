"""Immutable graph-diff DTOs for T6.09."""

from __future__ import annotations

from dataclasses import asdict, dataclass
from enum import Enum
from pathlib import Path
from typing import cast

type JsonValue = str | int | float | bool | None | tuple[JsonValue, ...] | tuple[tuple[str, JsonValue], ...]
type FrozenObject = tuple[tuple[str, JsonValue], ...]


class PostGraphStatus(Enum):
    AVAILABLE = "available"
    UNCHANGED = "unchanged"
    BLOCKED = "blocked"
    MISSING = "missing"
    INVALID = "invalid"


class EntityChangeType(Enum):
    ADDED = "added"
    REMOVED = "removed"
    CHANGED = "changed"
    UNCHANGED = "unchanged"


class RelationshipChangeType(Enum):
    ADDED = "added"
    REMOVED = "removed"
    CHANGED = "changed"
    UNCHANGED = "unchanged"


class CommunityChangeType(Enum):
    PRESERVED = "preserved"
    EXPANDED = "expanded"
    CONTRACTED = "contracted"
    SPLIT = "split"
    MERGED = "merged"
    REORGANIZED = "reorganized"
    ADDED = "added"
    REMOVED = "removed"


@dataclass(frozen=True, slots=True)
class FieldChange:
    """One semantic field-level change."""

    field_name: str
    before: JsonValue
    after: JsonValue


@dataclass(frozen=True, slots=True)
class RelationshipIdentity:
    """Stable relationship identity with optional parallel discriminator."""

    source_id: str
    target_id: str
    rel_type: str
    direction: str = "directed"
    parallel_key: str = ""


@dataclass(frozen=True, slots=True)
class GraphSnapshotRef:
    """Portable graph snapshot provenance."""

    portable_path: str = ""
    sha256: str = ""
    schema_version: str = ""
    entity_count: int = 0
    relationship_count: int = 0
    community_count: int = 0


@dataclass(frozen=True, slots=True)
class EntityChange:
    """One entity classification."""

    entity_id: str
    change: EntityChangeType
    before: FrozenObject = ()
    after: FrozenObject = ()
    field_changes: tuple[FieldChange, ...] = ()


@dataclass(frozen=True, slots=True)
class RelationshipChange:
    """One relationship classification."""

    identity: RelationshipIdentity
    change: RelationshipChangeType
    before: FrozenObject = ()
    after: FrozenObject = ()
    field_changes: tuple[FieldChange, ...] = ()


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
    pre_snapshot: GraphSnapshotRef = GraphSnapshotRef()
    post_snapshot: GraphSnapshotRef = GraphSnapshotRef()
    entity_changes: tuple[EntityChange, ...] = ()
    relationship_changes: tuple[RelationshipChange, ...] = ()
    community_changes: tuple[CommunityChange, ...] = ()
    limitations: tuple[str, ...] = ("Structural graph change is not proof of correctness.",)
    error_detail: str = ""

    def to_dict(self) -> dict[str, object]:
        """Return canonical JSON-serializable data."""
        return cast(dict[str, object], _normalize(asdict(self)))


@dataclass(frozen=True, slots=True)
class GraphDiffArtifacts:
    """Persisted graph-diff artifact paths and hashes."""

    json_path: Path
    markdown_path: Path
    graph_diff_hash: str
    markdown_hash: str


def _normalize(value: object) -> object:
    if isinstance(value, Enum):
        return value.value
    if isinstance(value, Path):
        return str(value)
    if isinstance(value, dict):
        return {k: _normalize(v) for k, v in value.items()}
    if isinstance(value, list | tuple):
        return [_normalize(v) for v in value]
    return value
