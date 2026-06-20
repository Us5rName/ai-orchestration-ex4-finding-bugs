"""Service wiring — constructs all concrete services from a config dict.

Extracted from Ex04SDK._build_services to keep sdk.py within the 150-line
limit while allowing the wiring logic to grow independently.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any

from ex04.services.agent.interface import AgentServiceInterface
from ex04.services.analysis.interface import AnalysisServiceInterface
from ex04.services.comparison.interface import ComparisonServiceInterface
from ex04.services.graph.interface import GraphServiceInterface
from ex04.services.vault.interface import VaultServiceInterface

ServiceTuple = tuple[
    GraphServiceInterface,
    VaultServiceInterface,
    AgentServiceInterface,
    ComparisonServiceInterface,
    AnalysisServiceInterface,
]


def build_services(config: dict[str, Any]) -> ServiceTuple:
    """Construct concrete service instances from a loaded config dict."""
    from ex04.services.agent import AgentService
    from ex04.services.analysis import AnalysisService
    from ex04.services.analysis.reverse_engineer import ReverseEngineer
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
        AnalysisService(reverse_engineer=ReverseEngineer(gatekeeper=gatekeeper, provider=provider)),
    )
