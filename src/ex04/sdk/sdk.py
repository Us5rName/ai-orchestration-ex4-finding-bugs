"""Single SDK entry point with dependency injection."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from ex04.sdk._comparison_inputs import discover_source_files, resolve_vault_dir
from ex04.sdk._comparison_ops import ComparisonOpsMixin
from ex04.sdk._extensions import ImpactReport, OrphanReport, analyze_patch_impact, detect_orphans
from ex04.sdk._wiring import build_services
from ex04.services.agent.interface import AgentServiceInterface
from ex04.services.analysis.interface import AnalysisServiceInterface
from ex04.services.comparison.interface import ComparisonServiceInterface
from ex04.services.graph.interface import GraphServiceInterface
from ex04.services.vault.interface import VaultServiceInterface
from ex04.shared.types import GraphData
from ex04.shared.types_metrics import ComparisonReport
from ex04.shared.types_results import InvestigationResult, PipelineResult


class Ex04SDK(ComparisonOpsMixin):
    """Single entry point for all EX04 operations. Delegates to services."""

    def __init__(
        self,
        graph: GraphServiceInterface,
        vault: VaultServiceInterface,
        agent: AgentServiceInterface,
        comparison: ComparisonServiceInterface,
        analysis: AnalysisServiceInterface,
        config: dict[str, Any] | None = None,
    ) -> None:
        """Inject service implementations and optional loaded config."""
        self._graph = graph
        self._vault = vault
        self._agent = agent
        self._comparison = comparison
        self._analysis = analysis
        self._config = config or {}

    @classmethod
    def from_config(cls, config_path: str) -> Ex04SDK:
        """Create a fully wired SDK from a JSON config file."""
        config = json.loads(Path(config_path).read_text(encoding="utf-8"))
        return cls(*build_services(config), config=config)

    def run_graphify(self, target_path: str) -> GraphData:
        """Extract and parse a code graph from the target codebase."""
        return self._graph_data(target_path)

    def build_vault(self, graph_data: GraphData) -> dict[str, Path]:
        """Build an Obsidian vault from parsed graph data."""
        return self._vault.build(graph_data)

    def investigate_bug(
        self, bug_report: str, graph_path: Path | None = None, vault_path: Path | None = None
    ) -> InvestigationResult:
        """Investigate a bug via the agent workflow (graph/vault optional)."""
        return self._agent.investigate(bug_report, graph_path, vault_path)

    def run_comparison(
        self,
        bug_report: str,
        source_files: list[Path],
        graph_data: GraphData | None = None,
        vault_path: Path | None = None,
    ) -> ComparisonReport:
        """Compare naive vs. graph-guided investigation approaches."""
        return self._legacy_comparison_report(bug_report, source_files, graph_data, vault_path)

    def reverse_engineer(self, target_path: str) -> str:
        """Reverse-engineer architecture docs from the target codebase."""
        return self._analysis.reverse_engineer(self._graph_data(target_path))

    def generate_report(self, investigation: InvestigationResult) -> str:
        """Generate a structured Markdown bug report from an investigation."""
        return self._analysis.report(investigation)

    def identify_patterns(self, target_path: str) -> list[str]:
        """Identify design patterns in the target codebase."""
        return self._analysis.identify_patterns(self._graph_data(target_path))

    def compare_target(self, target_path: str | Path, bug_report: str) -> ComparisonReport:
        """Extract graph, build vault, discover files, and run both comparison modes."""
        graph_data, vault_dir, source_files = self._comparison_inputs(target_path)
        return self._legacy_comparison_report(bug_report, source_files, graph_data, vault_dir)

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

    def full_pipeline(self, target_path: str, bug_report: str) -> PipelineResult:
        """Run the complete end-to-end pipeline into one aggregated result."""
        graph_path, graph_data = self._extract_graph(target_path)
        vault = self._vault.build(graph_data)
        vault_dir = resolve_vault_dir(vault)
        source_files = discover_source_files(target_path, self._config)
        investigation = self._agent.investigate(bug_report, graph_path, vault_dir)
        comparison = self._legacy_comparison_report(bug_report, source_files, graph_data, vault_dir)
        engineering = self._analysis.reverse_engineer(graph_data)
        bug_report_md = self._analysis.report(investigation)
        return PipelineResult(
            graph_result=str(graph_path),
            vault_result=str(vault.get("index", "")),
            investigation=investigation,
            comparison=comparison,
            engineering=engineering,
            bug_report_md=bug_report_md,
        )

    def _extract_graph(self, target_path: str | Path) -> tuple[Path, GraphData]:
        graph_path = self._graph.extract(str(target_path))
        return graph_path, self._graph.parse(graph_path)

    def _graph_data(self, target_path: str | Path) -> GraphData:
        return self._extract_graph(target_path)[1]

    def _comparison_inputs(self, target_path: str | Path) -> tuple[GraphData, Path | None, list[Path]]:
        graph_data = self._graph_data(target_path)
        vault_dir = resolve_vault_dir(self._vault.build(graph_data))
        source_files = discover_source_files(target_path, self._config)
        return graph_data, vault_dir, source_files

    def _legacy_comparison_report(
        self,
        bug_report: str,
        source_files: list[Path],
        graph_data: GraphData | None = None,
        vault_path: Path | None = None,
    ) -> ComparisonReport:
        result = self._comparison.run_comparison(bug_report, source_files, graph_data, vault_path)
        if isinstance(result, ComparisonReport):
            return result
        raise TypeError("legacy comparison call returned canonical outcome")
