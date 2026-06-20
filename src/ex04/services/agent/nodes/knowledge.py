"""Knowledge Load Node — loads graph + vault context into agent state.

Populates the graph_context and vault_context fields in AgentState
by reading from the graph data and vault files.

Implementation: **Phase 4** (T4.09)
"""

from __future__ import annotations

import logging

from ex04.services.agent.nodes.common import read_path_context
from ex04.services.agent.state import AgentState

logger = logging.getLogger(__name__)


class KnowledgeLoadNode:
    """Loads graph and vault context into the agent state.

    Reads graph summary and vault notes, then updates the state
    with the combined context for downstream nodes.

    Attributes:
        None — stateless node.
    """

    def __init__(self, context_limit: int = 8000) -> None:
        """Initialize with a maximum context character budget."""
        self.context_limit = context_limit

    def __call__(self, state: AgentState) -> AgentState:
        """Load context into state.

        Args:
            state: Current agent state.

        Returns:
            State with graph_context and vault_context populated.
        """
        logger.info("KnowledgeLoadNode: loading context")
        graph_context = read_path_context(state.get("graph_context", ""), self.context_limit)
        vault_context = read_path_context(state.get("vault_context", ""), self.context_limit)
        return {**state, "graph_context": graph_context, "vault_context": vault_context}
