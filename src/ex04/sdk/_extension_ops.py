"""SDK extension-operation mixin."""

from __future__ import annotations

from pathlib import Path

from ex04.sdk._extensions import (
    ImpactReport,
    OrphanReport,
    WeaknessConfig,
    WeaknessReport,
    analyze_patch_impact,
    detect_orphans,
    detect_weaknesses,
)
from ex04.shared.types import GraphData


class ExtensionOpsMixin:
    """Public SDK methods for repository-analysis extensions."""

    def detect_orphans(self, graph_data: GraphData, min_connections: int = 0) -> OrphanReport:
        """Detect orphan nodes and weakly connected components (EXT-1 / FR-7.5)."""
        return detect_orphans(graph_data, min_connections)

    def analyze_patch_impact(
        self,
        graph_data: GraphData,
        changed_symbols: list[str],
        max_depth: int = 3,
    ) -> ImpactReport:
        """Analyze transitive impact of a patch via BFS (EXT-2 / FR-7.6)."""
        return analyze_patch_impact(graph_data, changed_symbols, max_depth)

    def detect_weaknesses(
        self,
        graph_data: GraphData,
        config: WeaknessConfig | None = None,
        source_root: str | Path | None = None,
    ) -> WeaknessReport:
        """Detect generic graph/source weakness signals (FR-7.7 / T4.20)."""
        return detect_weaknesses(graph_data, config, source_root)
