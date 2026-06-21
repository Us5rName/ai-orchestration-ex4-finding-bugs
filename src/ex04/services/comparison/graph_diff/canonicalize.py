"""Canonical graph-diff values and hashing."""

from __future__ import annotations

import hashlib
import json
from collections.abc import Mapping

from ex04.services.comparison.graph_diff.models import FieldChange, FrozenObject, JsonValue
from ex04.services.graph.interface import GraphReaderInterface, RelationshipGraphView
from ex04.shared.types_graph_enums import EdgeDirection


def freeze_json(value: object) -> JsonValue:
    """Return deeply immutable JSON-compatible content."""
    if isinstance(value, Mapping):
        return tuple(sorted((str(k), freeze_json(v)) for k, v in value.items()))
    if isinstance(value, list | tuple):
        return tuple(freeze_json(v) for v in value)
    if isinstance(value, str | int | float | bool) or value is None:
        return value
    return str(value)


def object_from_pairs(pairs: Mapping[str, object]) -> FrozenObject:
    """Return sorted immutable key/value pairs."""
    return tuple(sorted((key, freeze_json(value)) for key, value in pairs.items()))


def entity_attributes(entity: object) -> FrozenObject:
    """Return semantic entity attributes used for change detection."""
    return object_from_pairs({
        "label": str(getattr(entity, "label", "") or getattr(entity, "entity_id", "")),
        "kind": str(getattr(entity, "kind", "")),
        "file_path": _portable_path(str(getattr(entity, "file_path", ""))),
        "line_range": tuple(getattr(entity, "line_range", (0, 0))),
        "metadata": getattr(entity, "metadata", {}) or {},
    })


def relationship_attributes(rel: RelationshipGraphView) -> FrozenObject:
    """Return semantic relationship attributes used for change detection."""
    return object_from_pairs({
        "confidence": rel.confidence,
        "confidence_score": rel.confidence_score,
        "weight": rel.weight,
        "source_anchor": _portable_path(rel.source_anchor or ""),
        "metadata": rel.metadata,
    })


def field_changes(before: FrozenObject, after: FrozenObject) -> tuple[FieldChange, ...]:
    """Return deterministic field-level changes between immutable objects."""
    left = dict(before)
    right = dict(after)
    changes = []
    for key in sorted(left.keys() | right.keys()):
        if left.get(key) != right.get(key):
            changes.append(FieldChange(key, left.get(key), right.get(key)))
    return tuple(changes)


def canonical_graph_hash(reader: GraphReaderInterface) -> str:
    """Return order-independent SHA-256 for a graph reader snapshot."""
    entities = tuple((node.entity_id, entity_attributes(node)) for node in reader.all_nodes())
    relationships = tuple(
        sorted(
            (
                rel.source_id,
                rel.target_id,
                rel.rel_type,
                rel.key,
                relationship_attributes(rel),
            )
            for node in reader.all_nodes()
            for rel in reader.edges_of(node.entity_id, direction=EdgeDirection.OUTGOING)
        )
    )
    communities = tuple(
        sorted((str(key), tuple(node.entity_id for node in nodes)) for key, nodes in reader.communities().items())
    )
    payload = {
        "entities": entities,
        "relationships": relationships,
        "communities": communities,
    }
    data = json.dumps(payload, sort_keys=True, separators=(",", ":"), default=str)
    return hashlib.sha256(data.encode("utf-8")).hexdigest()


def _portable_path(value: str) -> str:
    if not value:
        return ""
    normalized = value.replace("\\", "/")
    for marker in ("/src/", "/tests/", "/artifacts/"):
        if marker in normalized:
            return marker.strip("/") + "/" + normalized.split(marker, 1)[1]
    return normalized
