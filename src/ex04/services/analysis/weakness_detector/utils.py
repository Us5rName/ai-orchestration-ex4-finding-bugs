"""Shared helpers for weakness detector modules."""

from __future__ import annotations

import hashlib
import json
from collections.abc import Mapping

from ex04.services.analysis.weakness_detector.models import (
    EvidenceAnchor,
    EvidenceConfidence,
    RelationshipKey,
    ScoreComponents,
    Severity,
    WeaknessFinding,
    WeaknessSignal,
)
from ex04.services.graph.interface import GraphReaderInterface


def severity_for(score: float, boundaries: tuple[float, float, float, float]) -> Severity:
    """Map normalized score to severity."""
    if score >= boundaries[3]:
        return Severity.CRITICAL
    if score >= boundaries[2]:
        return Severity.HIGH
    if score >= boundaries[1]:
        return Severity.MEDIUM
    if score >= boundaries[0]:
        return Severity.LOW
    return Severity.INFO


def stable_id(signal: WeaknessSignal, parts: tuple[object, ...]) -> str:
    """Return stable content-derived finding ID."""
    payload = json.dumps([signal.value, *parts], sort_keys=True, default=str)
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()[:16]


def anchor(entity: object) -> EvidenceAnchor:
    """Create a typed anchor from an EntityView-like object."""
    start, end = tuple(getattr(entity, "line_range", (0, 0)))
    return EvidenceAnchor(
        file_path=str(getattr(entity, "file_path", "")),
        start_line=start or None,
        end_line=end or None,
        entity_id=str(getattr(entity, "entity_id", getattr(entity, "name", ""))),
    )


def relationship_key(rel: object) -> RelationshipKey:
    """Create a typed relationship key from a RelationshipView-like object."""
    return RelationshipKey(
        source_id=str(getattr(rel, "source_id", getattr(rel, "source", ""))),
        target_id=str(getattr(rel, "target_id", getattr(rel, "target", ""))),
        relationship_type=str(getattr(rel, "rel_type", getattr(rel, "type", ""))),
        parallel_key=str(getattr(rel, "key", "")) or None,
    )


def finding(
    *,
    signal: WeaknessSignal,
    tag: str,
    score: float,
    summary: str,
    entity_ids: tuple[str, ...],
    relationship_keys: tuple[RelationshipKey, ...] = (),
    evidence: tuple[EvidenceAnchor, ...] = (),
    confidence: EvidenceConfidence = EvidenceConfidence.INFERRED,
    limitations: tuple[str, ...] = (),
    boundaries: tuple[float, float, float, float] = (0.25, 0.5, 0.75, 0.9),
) -> WeaknessFinding:
    """Build a normalized WeaknessFinding."""
    normalized = max(0.0, min(1.0, score))
    return WeaknessFinding(
        finding_id=stable_id(signal, (tag, entity_ids, relationship_keys)),
        signal=signal,
        tag=tag,
        severity=severity_for(normalized, boundaries),
        confidence=confidence,
        score=normalized,
        summary=summary,
        entity_ids=tuple(sorted(entity_ids)),
        relationship_keys=relationship_keys,
        evidence=evidence,
        score_components=ScoreComponents(normalized, 0.5, 0.5),
        limitations=limitations,
    )


def graph_hash(reader: GraphReaderInterface) -> str:
    """Stable graph snapshot hash from GraphReader immutable views."""
    nodes = [
        {
            "entity_id": node.entity_id,
            "label": node.label,
            "kind": node.kind,
            "file_path": node.file_path,
            "line_range": node.line_range,
            "community": node.community,
            "metadata": _freeze_json(node.metadata),
        }
        for node in reader.all_nodes()
    ]
    rels = [
        {
            "source_id": rel.source_id,
            "target_id": rel.target_id,
            "rel_type": rel.rel_type,
            "key": rel.key,
            "confidence": rel.confidence,
            "confidence_score": rel.confidence_score,
            "weight": rel.weight,
            "source_anchor": rel.source_anchor,
            "metadata": _freeze_json(rel.metadata),
        }
        for node in reader.all_nodes()
        for rel in reader.edges_of(node.entity_id)
        if rel.source_id == node.entity_id
    ]
    payload = json.dumps({"nodes": nodes, "rels": rels}, sort_keys=True, default=str)
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()


def _freeze_json(value: object) -> object:
    if isinstance(value, Mapping):
        return tuple(sorted((str(key), _freeze_json(item)) for key, item in value.items()))
    if isinstance(value, list | tuple):
        return tuple(_freeze_json(item) for item in value)
    return value
