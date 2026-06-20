"""Patch Impact Analyzer — BFS traversal of reverse-dependency edges.

EXT-2 (FR-7.6): Given changed symbols, identify direct and transitive
dependents using the code graph. Graph reachability alone does not prove
runtime impact; this report is analytical only.

Traceability: [PRD-EXT §EXT-2], [TODO T7.08]
"""

from __future__ import annotations

from ex04.services.analysis.patch_impact_bfs import bfs_impact, build_reverse_edges
from ex04.services.analysis.patch_impact_types import ImpactedNode, ImpactReport
from ex04.shared.types import GraphData

_DEFAULT_MAX_DEPTH = 3

__all__ = ["PatchImpactAnalyzer", "ImpactReport", "ImpactedNode"]


class PatchImpactAnalyzer:
    """Analyze the potential impact of a patch using reverse-dependency BFS.

    Traverses the graph from changed symbols, collecting direct and
    transitive dependents up to max_depth. Cycle-safe via visited set.
    """

    def analyze(
        self,
        graph_data: GraphData,
        changed_symbols: list[str],
        max_depth: int = _DEFAULT_MAX_DEPTH,
    ) -> ImpactReport:
        """Return ImpactReport for the given changed symbols.

        Args:
            graph_data: Parsed Graphify output.
            changed_symbols: Names of entities changed by the patch.
            max_depth: BFS depth limit (0 = only changed, 1 = direct).

        Returns:
            ImpactReport with direct and transitive dependents.
        """
        if not changed_symbols:
            return ImpactReport(
                max_depth_used=max_depth,
                limitations=["No changed symbols provided."],
            )

        entity_map = {e.name: e for e in graph_data.entities}
        rev = build_reverse_edges(graph_data.relationships)

        direct: list[ImpactedNode] = []
        transitive: list[ImpactedNode] = []
        all_paths: list[list[str]] = []

        for symbol in changed_symbols:
            if symbol not in rev and symbol not in entity_map:
                continue
            bfs_impact(symbol, rev, entity_map, max_depth, direct, transitive, all_paths)

        affected_tests = [
            n.file_path
            for n in direct + transitive
            if n.file_path and ("test" in n.file_path.lower() or n.kind == "test")
        ]

        limitations = [
            "Graph reachability alone does not prove runtime impact.",
            f"BFS capped at depth {max_depth}.",
        ]
        symbols_not_found = [s for s in changed_symbols if s not in entity_map]
        if symbols_not_found:
            limitations.append(f"Symbols not in graph: {symbols_not_found}")

        return ImpactReport(
            changed_symbols=changed_symbols,
            direct_dependents=direct,
            transitive_dependents=transitive,
            affected_test_files=list(dict.fromkeys(affected_tests)),
            max_depth_used=max_depth,
            impact_paths=all_paths,
            limitations=limitations,
        )
