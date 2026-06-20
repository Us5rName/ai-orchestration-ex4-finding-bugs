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

from langgraph.graph import END, START, StateGraph

from ex04.services.agent.nodes.analysis import BugAnalysisNode
from ex04.services.agent.nodes.fix import FixGenerationNode
from ex04.services.agent.nodes.inspect import CodeInspectionNode
from ex04.services.agent.nodes.knowledge import KnowledgeLoadNode
from ex04.services.agent.nodes.rootcause import RootCauseNode
from ex04.services.agent.nodes.suspect import SuspectRankingNode
from ex04.services.agent.nodes.verify import VerificationNode
from ex04.services.agent.state import AgentState

logger = logging.getLogger(__name__)


class WorkflowBuilder:
    """Assembles the LangGraph debugging workflow.

    Registers all 7 investigation nodes and configures the control flow:
    a linear pipeline with a conditional retry loop from verify back
    to suspect when tests fail.

    Attributes:
        None — stateless builder.
    """

    @staticmethod
    def build() -> StateGraph:
        """Build and compile the LangGraph debugging workflow.

        Creates a StateGraph with AgentState, registers all 7 nodes,
        configures linear edges and the retry loop, then compiles
        the graph for execution.

        Returns:
            Compiled StateGraph ready for execution.
        """
        graph = StateGraph(AgentState)

        # Register all 7 nodes
        graph.add_node("knowledge", KnowledgeLoadNode())
        graph.add_node("analysis", BugAnalysisNode())
        graph.add_node("suspect", SuspectRankingNode())
        graph.add_node("inspect", CodeInspectionNode())
        graph.add_node("rootcause", RootCauseNode())
        graph.add_node("fix", FixGenerationNode())
        graph.add_node("verify", VerificationNode())

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
            WorkflowBuilder._verify_route,
            {"retry": "suspect", "pass": END},
        )

        compiled = graph.compile()
        logger.info("Compiled debugging workflow with 7 nodes")
        return compiled

    @staticmethod
    def _verify_route(state: AgentState) -> str:
        """Determine next step after verification.

        Routes to 'suspect' for retry if tests failed, or to END
        if tests passed.

        Args:
            state: Current agent state with test_results.

        Returns:
            'retry' to loop back to suspect, or 'pass' to end.
        """
        test_results = state.get("test_results", {})
        failed = test_results.get("failed", 0)

        if failed > 0:
            return "retry"
        return "pass"
