"""Single SDK entry point with dependency injection.

All business logic flows through this module. CLI, GUI, and REST layers
delegate here — they never import internal domain services directly.

The SDK depends only on the five service *interfaces* (ADR-005), so it can be
constructed and tested with mocks without any concrete service implemented.
``Ex04SDK.from_config`` is the single place that performs concrete wiring; see
``docs/PHASE5_INTEGRATION.md`` for how Phase 4 plugs in.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from ex04.services.agent.interface import AgentServiceInterface
from ex04.services.analysis.interface import AnalysisServiceInterface
from ex04.services.comparison.interface import ComparisonServiceInterface
from ex04.services.graph.interface import GraphServiceInterface
from ex04.services.vault.interface import VaultServiceInterface
from ex04.shared.types import GraphData
from ex04.shared.types_metrics import ComparisonReport
from ex04.shared.types_results import InvestigationResult, PipelineResult

ServiceTuple = tuple[
    GraphServiceInterface,
    VaultServiceInterface,
    AgentServiceInterface,
    ComparisonServiceInterface,
    AnalysisServiceInterface,
]


class Ex04SDK:
    """Single entry point for all EX04 operations.

    Orchestrates the graph, vault, agent, comparison, and analysis services.
    Holds no business logic — every method delegates to exactly one service
    (or composes a few for ``full_pipeline``).
    """

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
        return cls(*cls._build_services(config), config=config)

    @staticmethod
    def _build_services(config: dict[str, Any]) -> ServiceTuple:
        """Construct concrete services from config."""
        from ex04.services.agent import AgentService
        from ex04.services.analysis import AnalysisService
        from ex04.services.comparison import ComparisonService
        from ex04.services.graph import GraphService
        from ex04.services.vault import VaultService
        from ex04.shared.gatekeeper import ApiGatekeeper

        vault_path = Path(config.get("vault", {}).get("output_dir", "./obsidian"))
        target_path = Path(config.get("paths", {}).get("target_codebase", "."))
        agent_config = config.get("agent", {})
        provider_config = config.get("provider", {})
        provider = provider_config.get("name", "openai")
        gatekeeper = ApiGatekeeper(
            rate_limits_path="config/rate_limits.json",
            provider_configs={provider: provider_config},
        )
        return (
            GraphService(),
            VaultService(vault_path),
            AgentService(
                target_path,
                max_iterations=int(agent_config.get("max_iterations", 5)),
                max_suspects=int(agent_config.get("max_suspects", 5)),
                context_limit=int(agent_config.get("context_window_tokens", 8000)),
                gatekeeper=gatekeeper,
                provider=provider,
            ),
            ComparisonService(gatekeeper, provider),
            AnalysisService(),
        )

    def run_graphify(self, target_path: str) -> GraphData:
        """Extract and parse a code graph from the target codebase."""
        graph_path = self._graph.extract(target_path)
        return self._graph.parse(graph_path)

    def build_vault(self, graph_data: GraphData) -> dict[str, Path]:
        """Build an Obsidian vault from parsed graph data."""
        return self._vault.build(graph_data)

    def investigate_bug(
        self,
        bug_report: str,
        graph_path: Path | None = None,
        vault_path: Path | None = None,
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
        return self._comparison.run_comparison(
            bug_report, source_files, graph_data, vault_path
        )

    def reverse_engineer(self, target_path: str) -> str:
        """Reverse-engineer architecture docs from the target codebase."""
        graph_data = self.run_graphify(target_path)
        return self._analysis.reverse_engineer(graph_data)

    def full_pipeline(self, target_path: str, bug_report: str) -> PipelineResult:
        """Run the complete end-to-end pipeline into one aggregated result."""
        graph_path = self._graph.extract(target_path)
        graph_data = self._graph.parse(graph_path)
        vault = self._vault.build(graph_data)
        investigation = self._agent.investigate(bug_report, graph_path)
        comparison = self._comparison.run_comparison(bug_report, [], graph_data)
        engineering = self._analysis.reverse_engineer(graph_data)
        return PipelineResult(
            graph_result=str(graph_path),
            vault_result=str(vault.get("index", "")),
            investigation=investigation,
            comparison=comparison,
            engineering=engineering,
        )
