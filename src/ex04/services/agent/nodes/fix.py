"""Fix Generation Node — proposes and applies code fix.

Generates a fix based on the root cause analysis and applies
it to the target file.

Implementation: **Phase 4** (T4.14)
"""

from __future__ import annotations

import logging

from ex04.services.agent.state import AgentState

logger = logging.getLogger(__name__)


class FixGenerationNode:
    """Generates and applies a code fix.

    Uses the gatekeeper to call the LLM with the root cause
    and produces a proposed fix, then applies it.

    Attributes:
        None — stateless node.
    """

    def __call__(self, state: AgentState) -> AgentState:
        """Generate and apply fix.

        Args:
            state: Current agent state.

        Returns:
            State with proposed_fix and fix_applied populated.
        """
        logger.info("FixGenerationNode: generating fix")
        return state
