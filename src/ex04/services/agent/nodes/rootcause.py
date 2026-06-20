"""Root Cause Node — determines exact bug origin.

Analyzes the inspected code to determine the root cause
of the bug and populates the root_cause field.

Implementation: **Phase 4** (T4.13)
"""

from __future__ import annotations

import logging

from ex04.services.agent.state import AgentState

logger = logging.getLogger(__name__)


class RootCauseNode:
    """Determines the root cause from inspected code.

    Uses the gatekeeper to call the LLM with the inspected
    code and produces a structured root cause description.

    Attributes:
        None — stateless node.
    """

    def __call__(self, state: AgentState) -> AgentState:
        """Determine root cause.

        Args:
            state: Current agent state.

        Returns:
            State with root_cause populated.
        """
        logger.info("RootCauseNode: determining root cause")
        return state
