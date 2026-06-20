"""Code Inspection Node — fetches relevant code snippets.

Fetches code snippets for the top-ranked suspects and records
files read for comparison metrics.

Implementation: **Phase 4** (T4.12)
"""

from __future__ import annotations

import logging

from ex04.services.agent.state import AgentState

logger = logging.getLogger(__name__)


class CodeInspectionNode:
    """Fetches code snippets for ranked suspects.

    Reads the source files for each suspect location and
    populates the inspected_code field.

    Attributes:
        None — stateless node.
    """

    def __call__(self, state: AgentState) -> AgentState:
        """Inspect code for suspects.

        Args:
            state: Current agent state.

        Returns:
            State with inspected_code populated.
        """
        logger.info("CodeInspectionNode: inspecting code")
        return state
