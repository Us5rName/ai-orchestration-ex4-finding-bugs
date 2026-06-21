"""Agent Workflow — assembles the LangGraph debugging state machine."""

from __future__ import annotations

import logging
from collections.abc import Callable
from pathlib import Path

from langgraph.graph import END, START, StateGraph
from langgraph.graph.state import CompiledStateGraph

from ex04.services.agent.deps import NodeDeps
from ex04.services.agent.nodes.analysis import build_analysis_node
from ex04.services.agent.nodes.fix import build_fix_node
from ex04.services.agent.nodes.inspect import build_inspect_node
from ex04.services.agent.nodes.knowledge import KnowledgeLoadNode
from ex04.services.agent.nodes.rootcause import build_rootcause_node
from ex04.services.agent.nodes.suspect import SuspectRankingNode
from ex04.services.agent.nodes.verify import VerificationNode
from ex04.services.agent.state import AgentState
from ex04.shared.gatekeeper import GatekeeperInterface

logger = logging.getLogger(__name__)

# Fallback when the caller does not supply config.agent.max_iterations.
_DEFAULT_MAX_ITERATIONS = 5

NODE_SEQUENCE = ("knowledge", "analysis", "suspect", "inspect", "rootcause", "fix", "verify")


def build_nodes(deps: NodeDeps) -> dict[str, Callable[[AgentState], AgentState]]:
    """Build workflow nodes from the shared dependency bundle."""
    return {
        "knowledge": KnowledgeLoadNode(
            context_limit=deps.context_limit,
            target_path=deps.target_path,
        ),
        "analysis": build_analysis_node(deps),
        "suspect": SuspectRankingNode(max_suspects=deps.max_suspects),
        "inspect": build_inspect_node(deps),
        "rootcause": build_rootcause_node(deps),
        "fix": build_fix_node(deps),
        "verify": VerificationNode(command=deps.test_command, cwd=deps.target_path),
    }


def add_linear_edges(graph: StateGraph, sequence: tuple[str, ...] = NODE_SEQUENCE) -> None:
    """Register START and linear workflow edges."""
    graph.add_edge(START, sequence[0])
    for source, target in zip(sequence, sequence[1:], strict=False):
        graph.add_edge(source, target)


def add_retry_edge(graph: StateGraph, route: Callable[[AgentState], str]) -> None:
    """Register the verify retry edge."""
    graph.add_conditional_edges("verify", route, {"retry": "suspect", "pass": END})


class WorkflowBuilder:
    """Assembles the linear workflow and bounded verify retry loop."""

    def __init__(
        self,
        target_path: Path | str = ".",
        max_iterations: int = _DEFAULT_MAX_ITERATIONS,
        max_suspects: int = 5,
        context_limit: int = 8000,
        gatekeeper: GatekeeperInterface | None = None,
        provider: str = "openai",
        test_command: list[str] | None = None,
    ) -> None:
        """Initialize with a retry cap.

        Args:
            max_iterations: Maximum verify→suspect retry cycles. The agent
                service should pass ``config['agent']['max_iterations']``.
        """
        self.target_path = Path(target_path)
        self.max_iterations = max_iterations
        self.max_suspects = max_suspects
        self.context_limit = context_limit
        self.gatekeeper = gatekeeper
        self.provider = provider
        self.test_command = test_command or ["uv", "run", "pytest", "-q"]
        self.deps = NodeDeps(
            gatekeeper=gatekeeper,
            provider=provider,
            target_path=self.target_path,
            context_limit=context_limit,
            max_suspects=max_suspects,
            test_command=self.test_command,
        )

    def build(self) -> CompiledStateGraph:
        """Build and compile the LangGraph debugging workflow."""
        graph = StateGraph(AgentState)

        for name, node in build_nodes(self.deps).items():
            graph.add_node(name, node)
        add_linear_edges(graph)
        add_retry_edge(graph, self._verify_route)

        compiled = graph.compile()
        logger.info(
            "Compiled debugging workflow with 7 nodes (max_iterations=%d)", self.max_iterations
        )
        return compiled

    def _verify_route(self, state: AgentState) -> str:
        """Route to retry while tests fail and the retry budget remains."""
        failed = state.get("test_results", {}).get("failed", 0)
        iterations = state.get("iterations", 0)

        if failed > 0 and iterations < self.max_iterations:
            return "retry"
        return "pass"
