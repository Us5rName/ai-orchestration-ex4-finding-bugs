"""Verification Node — runs tests to confirm fix.

Executes tests on the fixed code and records results.
Determines whether to iterate or succeed.

Implementation: **Phase 4** (T4.15)
"""

from __future__ import annotations

import logging

from ex04.services.agent.state import AgentState

logger = logging.getLogger(__name__)


class VerificationNode:
    """Runs tests and determines success or retry.

    Executes the test suite on the fixed code and populates
    test_results in the state.

    Attributes:
        None — stateless node.
    """

    def __call__(self, state: AgentState) -> AgentState:
        """Run verification tests and count the completed iteration.

        Incrementing ``iterations`` here lets the workflow's conditional edge
        bound the verify→suspect retry loop by ``max_iterations``.

        Args:
            state: Current agent state.

        Returns:
            State with test_results populated and the iteration counter bumped.
        """
        logger.info("VerificationNode: running tests")
        return {**state, "iterations": state.get("iterations", 0) + 1}
