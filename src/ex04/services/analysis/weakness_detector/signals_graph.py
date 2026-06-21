"""Graph-only weakness signals."""

from __future__ import annotations

from ex04.services.analysis.weakness_detector.config import WeaknessConfig
from ex04.services.analysis.weakness_detector.models import (
    EvidenceConfidence,
    WeaknessFinding,
    WeaknessSignal,
)
from ex04.services.analysis.weakness_detector.source_index import SourceIndex
from ex04.services.analysis.weakness_detector.utils import anchor, finding, relationship_key
from ex04.services.graph.interface import GraphReaderInterface, RelationshipGraphView
from ex04.shared.graph_ops import connected_components
from ex04.shared.types import Entity, GraphData, Relationship
from ex04.shared.types_graph_enums import EdgeDirection


def high_degree_signal(
    *, reader: GraphReaderInterface, source_index: SourceIndex, config: WeaknessConfig
) -> tuple[WeaknessFinding, ...]:
    """Detect entities at or above the configured degree threshold."""
    del source_index
    rows = []
    for entity, degree in reader.top_n_by_degree(max(config.max_high_degree_findings, 0)):
        if degree >= config.degree_threshold:
            rows.append(finding(
                signal=WeaknessSignal.HIGH_DEGREE,
                tag=f"degree:{degree}",
                score=min(1.0, degree / max(config.degree_threshold, 1)),
                summary=f"{entity.label or entity.entity_id} has measured graph degree {degree}.",
                entity_ids=(entity.entity_id,),
                evidence=(anchor(entity),),
                confidence=EvidenceConfidence.EXTRACTED,
                limitations=("High degree alone does not prove a defect.",),
                boundaries=config.severity_boundaries,
            ))
    return tuple(rows)


def isolated_component_signal(
    *, reader: GraphReaderInterface, source_index: SourceIndex, config: WeaknessConfig
) -> tuple[WeaknessFinding, ...]:
    """Detect small weak components using the shared component primitive."""
    del source_index
    graph = _graph_data_from_reader(reader)
    findings = []
    for members in connected_components(graph.entities, graph.relationships):
        if len(members) <= config.weak_component_max_size:
            findings.append(finding(
                signal=WeaknessSignal.ISOLATED_COMPONENT,
                tag="component",
                score=1.0 if len(members) == 1 else 0.6,
                summary=f"Weak component contains {len(members)} entity/entities: {', '.join(members)}.",
                entity_ids=tuple(members),
                confidence=EvidenceConfidence.EXTRACTED,
                limitations=("Low connectivity is not proof of a defect.",),
                boundaries=config.severity_boundaries,
            ))
    return tuple(findings)


def relationship_confidence_signal(
    *, reader: GraphReaderInterface, source_index: SourceIndex, config: WeaknessConfig
) -> tuple[WeaknessFinding, ...]:
    """Detect ambiguous, inferred, unknown, or low-confidence relationships."""
    del source_index
    results = []
    for rel in _outgoing_relationships(reader):
        state = (rel.confidence or "unknown").lower()
        low_score = rel.confidence_score is not None and rel.confidence_score < config.confidence_threshold
        uncertain = state in {"ambiguous", "inferred"} or low_score
        unknown = state == "unknown" and config.include_missing_confidence
        if not (uncertain or unknown):
            continue
        confidence = _confidence_for_state(state)
        score = 1.0 - (rel.confidence_score or 0.0) if rel.confidence_score is not None else 0.65
        results.append(finding(
            signal=WeaknessSignal.RELATIONSHIP_CONFIDENCE,
            tag=state,
            score=score,
            summary=_relationship_summary(rel, state),
            entity_ids=(rel.source_id, rel.target_id),
            relationship_keys=(relationship_key(rel),),
            confidence=confidence,
            limitations=("Uncertain graph evidence requires source validation.",),
            boundaries=config.severity_boundaries,
        ))
    return tuple(results)


def _outgoing_relationships(reader: GraphReaderInterface) -> tuple[RelationshipGraphView, ...]:
    rels: list[RelationshipGraphView] = []
    for node in reader.all_nodes():
        rels.extend(reader.edges_of(node.entity_id, direction=EdgeDirection.OUTGOING))
    return tuple(sorted(rels, key=lambda r: r.key))


def _graph_data_from_reader(reader: GraphReaderInterface) -> GraphData:
    entities = [
        Entity(n.entity_id, n.kind, n.file_path, n.line_range, n.label, n.community, dict(n.metadata))
        for n in reader.all_nodes()
    ]
    rels = [
        Relationship(r.source_id, r.target_id, r.rel_type, r.key, r.confidence,
                     r.confidence_score, r.weight, r.source_anchor, dict(r.metadata))
        for r in _outgoing_relationships(reader)
    ]
    return GraphData(entities=entities, relationships=rels)


def _confidence_for_state(state: str) -> EvidenceConfidence:
    if state == "extracted":
        return EvidenceConfidence.EXTRACTED
    if state == "ambiguous":
        return EvidenceConfidence.AMBIGUOUS
    if state == "inferred":
        return EvidenceConfidence.INFERRED
    return EvidenceConfidence.UNKNOWN


def _relationship_summary(rel: RelationshipGraphView, state: str) -> str:
    if state == "inferred":
        return f"Relationship {rel.source_id}->{rel.target_id} is inferred and should be validated."
    if state == "ambiguous":
        return f"Relationship {rel.source_id}->{rel.target_id} is ambiguous and needs review."
    return f"Relationship {rel.source_id}->{rel.target_id} has unknown or low confidence."
