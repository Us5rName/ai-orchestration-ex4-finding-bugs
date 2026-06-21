"""Canonical identity and attribute helpers for graph diffing."""

from __future__ import annotations

from typing import Any

from ex04.services.comparison.graph_diff.models import RelationshipIdentity


def entity_attributes(entity: object) -> dict[str, Any]:
    """Return entity attributes that participate in entity change detection."""
    return {
        "label": str(getattr(entity, "label", "") or getattr(entity, "name", "")),
        "kind": str(getattr(entity, "kind", "")),
        "file_path": str(getattr(entity, "file_path", "")),
        "line_range": list(getattr(entity, "line_range", (0, 0))),
        "metadata": dict(getattr(entity, "metadata", {}) or {}),
    }


def relationship_identity(relationship: object) -> RelationshipIdentity:
    """Return stable relationship identity from source, target, type, and direction."""
    return RelationshipIdentity(
        source_id=str(getattr(relationship, "source", "")),
        target_id=str(getattr(relationship, "target", "")),
        rel_type=str(getattr(relationship, "type", "")),
    )


def relationship_attributes(relationship: object) -> dict[str, Any]:
    """Return non-identity relationship attributes used for change detection."""
    return {
        "confidence": getattr(relationship, "confidence", None),
        "confidence_score": getattr(relationship, "confidence_score", None),
        "weight": getattr(relationship, "weight", None),
        "source_anchor": getattr(relationship, "source_anchor", None),
        "metadata": dict(getattr(relationship, "metadata", {}) or {}),
    }
