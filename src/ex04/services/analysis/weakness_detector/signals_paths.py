"""Expected dependency-path weakness signal."""

from __future__ import annotations

from collections import deque

from ex04.services.analysis.weakness_detector.config import WeaknessConfig
from ex04.services.analysis.weakness_detector.models import (
    EvidenceConfidence,
    WeaknessFinding,
    WeaknessSignal,
)
from ex04.services.analysis.weakness_detector.source_index import SourceIndex
from ex04.services.analysis.weakness_detector.utils import finding
from ex04.services.graph.interface import GraphReaderInterface
from ex04.shared.types_graph_enums import EdgeDirection


def broken_path_signal(
    *, reader: GraphReaderInterface, source_index: SourceIndex, config: WeaknessConfig
) -> tuple[WeaknessFinding, ...]:
    """Detect configured expected directed paths that are not reachable."""
    del source_index
    results = []
    nodes = {node.entity_id for node in reader.all_nodes()}
    for req in config.expected_paths:
        if req.source_id not in nodes or req.target_id not in nodes:
            raise ValueError(f"unknown dependency path endpoint: {req.source_id}->{req.target_id}")
        if _reachable(reader, req.source_id, req.target_id,
                      set(req.allowed_relationship_types), req.max_depth):
            continue
        results.append(finding(
            signal=WeaknessSignal.BROKEN_DEPENDENCY_PATH,
            tag="expected_path",
            score=0.8,
            summary=f"Expected directed path {req.source_id}->{req.target_id} is not reachable.",
            entity_ids=(req.source_id, req.target_id),
            confidence=EvidenceConfidence.EXTRACTED,
            limitations=("Missing configured reachability is not proof of a runtime defect.",),
            boundaries=config.severity_boundaries,
        ))
    return tuple(results)


def _reachable(
    reader: GraphReaderInterface,
    source_id: str,
    target_id: str,
    allowed_types: set[str],
    max_depth: int | None,
) -> bool:
    queue: deque[tuple[str, int]] = deque([(source_id, 0)])
    visited = {source_id}
    while queue:
        current, depth = queue.popleft()
        if current == target_id:
            return True
        if max_depth is not None and depth >= max_depth:
            continue
        for rel in reader.edges_of(current, direction=EdgeDirection.OUTGOING):
            if allowed_types and rel.rel_type not in allowed_types:
                continue
            if rel.target_id not in visited:
                visited.add(rel.target_id)
                queue.append((rel.target_id, depth + 1))
    return False
