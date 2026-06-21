"""Root Cause Node — determines exact bug origin.

Analyzes the inspected code to determine the root cause
of the bug and populates the root_cause field.

Implementation: **Phase 4** (T4.13)
"""

from __future__ import annotations

import logging

from ex04.services.agent.deps import NodeDeps
from ex04.services.agent.nodes import common
from ex04.services.agent.state import AgentState
from ex04.shared.gatekeeper import GatekeeperInterface

logger = logging.getLogger(__name__)


class RootCauseNode:
    """Determines the root cause from inspected code.

    Uses the gatekeeper to call the LLM with the inspected
    code and produces a structured root cause description.

    Attributes:
        None — stateless node.
    """

    def __init__(self, gatekeeper: GatekeeperInterface | None = None, provider: str = "openai") -> None:
        """Initialize with optional Gatekeeper dependency."""
        self.deps = NodeDeps(gatekeeper=gatekeeper, provider=provider)

    def __call__(self, state: AgentState) -> AgentState:
        """Determine root cause.

        Args:
            state: Current agent state.

        Returns:
            State with root_cause populated.
        """
        logger.info("RootCauseNode: determining root cause")
        prompt = (
            "Explain the root cause using only the inspected code.\n"
            f"Bug:\n{state.get('bug_report', '')}\n\nCode:\n{state.get('inspected_code', '')}"
        )
        response = common.call_llm(self.deps, state, "rootcause", prompt)
        root_cause = response.text.strip() or "Root cause could not be determined."
        return {**common.state_with_tokens(state, response), "root_cause": root_cause}


def build_rootcause_node(deps: NodeDeps) -> RootCauseNode:
    """Build the root-cause node from workflow dependencies."""
    return RootCauseNode(deps.gatekeeper, deps.provider)
