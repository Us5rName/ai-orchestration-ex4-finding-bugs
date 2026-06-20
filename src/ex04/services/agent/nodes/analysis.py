"""Bug Analysis Node — analyzes bug report against graph context.

Analyzes the bug report using graph context and produces initial
suspect candidates via LLM call through the gatekeeper.

Implementation: **Phase 4** (T4.10)
"""

from __future__ import annotations

import logging

from ex04.services.agent.nodes.common import call_gatekeeper, merge_tokens, parse_suspects
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
        self.gatekeeper = gatekeeper
        self.provider = provider

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
            f"Bug:\n{state.get('bug_report', '')}\n\nGraph:\n{state.get('graph_context', '')}"
        )
        response = call_gatekeeper(self.gatekeeper, self.provider, prompt)
        suspects = parse_suspects(response.text) or state.get("suspects", [])
        return {**state, "suspects": suspects, "token_usage": merge_tokens(state, response)}
