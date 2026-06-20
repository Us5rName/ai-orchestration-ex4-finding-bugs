"""Knowledge Load Node — loads graph + vault context into agent state.

Populates the graph_context and vault_context fields in AgentState
by reading from the graph data and vault files.

Implementation: **Phase 4** (T4.09)
"""

from __future__ import annotations

import logging

from ex04.services.agent.state import AgentState

logger = logging.getLogger(__name__)


class KnowledgeLoadNode:
    """Loads graph and vault context into the agent state.

    Reads graph summary and vault notes, then updates the state
    with the combined context for downstream nodes.

    Attributes:
        None — stateless node.
    """

    def __call__(self, state: AgentState) -> AgentState:
        """Load context into state.

        Args:
            state: Current agent state.

        Returns:
            State with graph_context and vault_context populated.
        """
        logger.info("KnowledgeLoadNode: loading context")
        return state
