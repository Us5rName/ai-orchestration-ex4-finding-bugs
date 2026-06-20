"""Graph-analysis extension operations exposed through the SDK.

EXT-1 (FR-7.5): Orphan / weak-component detection.
EXT-2 (FR-7.6): Patch-impact analysis.

Traceability: [PRD-EXT], [TODO T7.07, T7.08]
"""

from __future__ import annotations

from ex04.services.analysis.orphan_detector import OrphanDetector, OrphanReport
from ex04.services.analysis.patch_impact import ImpactReport, PatchImpactAnalyzer
from ex04.shared.types import GraphData

__all__ = ["detect_orphans", "analyze_patch_impact", "OrphanReport", "ImpactReport"]


def detect_orphans(graph_data: GraphData, min_connections: int = 0) -> OrphanReport:
    """Detect orphan nodes and weakly connected components (EXT-1, FR-7.5).

    Args:
        graph_data: Parsed Graphify output.
        min_connections: Degree threshold — nodes at or below are orphan candidates.

    Returns:
        OrphanReport with orphan nodes, weak components, and limitations.
    """
    return OrphanDetector().detect(graph_data, min_connections)


def analyze_patch_impact(
    graph_data: GraphData,
    changed_symbols: list[str],
    max_depth: int = 3,
) -> ImpactReport:
    """Analyze transitive impact of a patch (EXT-2, FR-7.6).

    Args:
        graph_data: Parsed Graphify output.
        changed_symbols: Names of entities modified by the patch.
        max_depth: BFS traversal depth limit.

    Returns:
        ImpactReport with direct and transitive dependents.
    """
    return PatchImpactAnalyzer().analyze(graph_data, changed_symbols, max_depth)
