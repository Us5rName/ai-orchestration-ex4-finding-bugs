"""Agent Workflow — assembles LangGraph state machine for debugging.

Builds a LangGraph StateGraph with 7 nodes implementing the bug
investigation pipeline: knowledge → analysis → suspect → inspect →
rootcause → fix → verify, with a retry loop from verify back to suspect.

## Contract (AgentServiceInterface)

| Method | Input | Output | Phase |
|---|---|---|---|
| `build()` | — | StateGraph | P4 |

Implementation: **Phase 4** (T4.08)
"""

from __future__ import annotations

import logging
from pathlib import Path

from langgraph.graph import END, START, StateGraph
from langgraph.graph.state import CompiledStateGraph

from ex04.services.agent.nodes.analysis import BugAnalysisNode
from ex04.services.agent.nodes.fix import FixGenerationNode
from ex04.services.agent.nodes.inspect import CodeInspectionNode
from ex04.services.agent.nodes.knowledge import KnowledgeLoadNode
from ex04.services.agent.nodes.rootcause import RootCauseNode
from ex04.services.agent.nodes.suspect import SuspectRankingNode
from ex04.services.agent.nodes.verify import VerificationNode
from ex04.services.agent.state import AgentState
from ex04.shared.gatekeeper import GatekeeperInterface

logger = logging.getLogger(__name__)

# Fallback when the caller does not supply config.agent.max_iterations.
_DEFAULT_MAX_ITERATIONS = 5


class WorkflowBuilder:
    """Assembles the LangGraph debugging workflow.

    Registers all 7 investigation nodes and configures the control flow:
    a linear pipeline with a conditional retry loop from verify back to
    suspect when tests fail, bounded by ``max_iterations``.

    Attributes:
        max_iterations: Cap on verify→suspect retries before forcing END.
    """

    def __init__(
        self,
        target_path: Path | str = ".",
        max_iterations: int = _DEFAULT_MAX_ITERATIONS,
        max_suspects: int = 5,
        context_limit: int = 8000,
        gatekeeper: GatekeeperInterface | None = None,
        provider: str = "openai",
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

    def build(self) -> CompiledStateGraph:
        """Build and compile the LangGraph debugging workflow.

        Creates a StateGraph with AgentState, registers all 7 nodes,
        configures linear edges and the retry loop, then compiles
        the graph for execution.

        Returns:
            Compiled graph ready for execution.
        """
        graph = StateGraph(AgentState)

        # Register all 7 nodes
        graph.add_node("knowledge", KnowledgeLoadNode(context_limit=self.context_limit))
        graph.add_node("analysis", BugAnalysisNode(self.gatekeeper, self.provider))
        graph.add_node("suspect", SuspectRankingNode(max_suspects=self.max_suspects))
        graph.add_node("inspect", CodeInspectionNode(self.target_path))
        graph.add_node("rootcause", RootCauseNode(self.gatekeeper, self.provider))
        graph.add_node("fix", FixGenerationNode(self.target_path, self.gatekeeper, self.provider))
        graph.add_node("verify", VerificationNode(cwd=self.target_path))

        # Linear control flow
        graph.add_edge(START, "knowledge")
        graph.add_edge("knowledge", "analysis")
        graph.add_edge("analysis", "suspect")
        graph.add_edge("suspect", "inspect")
        graph.add_edge("inspect", "rootcause")
        graph.add_edge("rootcause", "fix")
        graph.add_edge("fix", "verify")

        # Conditional retry: verify → suspect (if tests fail) or END
        graph.add_conditional_edges(
            "verify",
            self._verify_route,
            {"retry": "suspect", "pass": END},
        )

        compiled = graph.compile()
        logger.info(
            "Compiled debugging workflow with 7 nodes (max_iterations=%d)", self.max_iterations
        )
        return compiled

    def _verify_route(self, state: AgentState) -> str:
        """Determine next step after verification.

        Routes to 'suspect' to retry when tests still fail and the retry
        budget is not exhausted; otherwise routes to END. Bounding by
        ``max_iterations`` prevents an unbounded loop (and the resulting
        LangGraph GraphRecursionError) when a fix never passes.

        Args:
            state: Current agent state with test_results and iterations.

        Returns:
            'retry' to loop back to suspect, or 'pass' to end.
        """
        failed = state.get("test_results", {}).get("failed", 0)
        iterations = state.get("iterations", 0)

        if failed > 0 and iterations < self.max_iterations:
            return "retry"
        return "pass"
