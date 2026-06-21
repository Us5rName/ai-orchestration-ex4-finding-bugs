"""Bug Analysis Node — analyzes bug report against graph context.

Analyzes the bug report using graph context and produces initial
suspect candidates via LLM call through the gatekeeper.

Implementation: **Phase 4** (T4.10)
"""

from __future__ import annotations

import logging

from ex04.services.agent.deps import NodeDeps
from ex04.services.agent.nodes import common
from ex04.services.agent.state import AgentState
from ex04.shared.gatekeeper import GatekeeperInterface

logger = logging.getLogger(__name__)


class BugAnalysisNode:
    """Analyzes the bug report and produces initial suspects.

    Uses the gatekeeper to call the LLM with the bug report and
    graph context, then populates the suspects field.

    Attributes:
        None — stateless node.
    """

    def __init__(self, gatekeeper: GatekeeperInterface | None = None, provider: str = "openai") -> None:
        """Initialize with optional Gatekeeper dependency."""
        self.deps = NodeDeps(gatekeeper=gatekeeper, provider=provider)

    def __call__(self, state: AgentState) -> AgentState:
        """Analyze bug and produce suspects.

        Args:
            state: Current agent state.

        Returns:
            State with suspects populated.
        """
        logger.info("BugAnalysisNode: analyzing bug report")
        prompt = (
            "Identify suspect Python locations as file.py:line-line.\n"
            f"Bug:\n{state.get('bug_report', '')}\n\nContext:\n{common.context_for_prompt(state)}"
        )
        response = common.call_llm(self.deps, state, "analysis", prompt)
        suspects = common.parse_suspects(response.text) or state.get("suspects", [])
        return {**common.state_with_tokens(state, response), "suspects": suspects}


def build_analysis_node(deps: NodeDeps) -> BugAnalysisNode:
    """Build the analysis node from workflow dependencies."""
    return BugAnalysisNode(deps.gatekeeper, deps.provider)
