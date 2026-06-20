"""Suspect Ranking Node — ranks candidates by centrality.

Ranks suspect locations using graph centrality metrics and
proximity to failure indicators.

Implementation: **Phase 4** (T4.11)
"""

from __future__ import annotations

import logging

from ex04.services.agent.state import AgentState

logger = logging.getLogger(__name__)


class SuspectRankingNode:
    """Ranks suspects by graph centrality and proximity.

    Uses the GraphAnalyzer to compute centrality scores and
    re-ranks the suspects list.

    Attributes:
        None — stateless node.
    """

    def __init__(self, max_suspects: int = 5) -> None:
        """Initialize with the maximum suspects retained."""
        self.max_suspects = max_suspects

    def __call__(self, state: AgentState) -> AgentState:
        """Rank suspects by centrality.

        Args:
            state: Current agent state.

        Returns:
            State with suspects re-ranked.
        """
        logger.info("SuspectRankingNode: ranking suspects")
        terms = state.get("bug_report", "").lower().split()
        ranked = sorted(
            state.get("suspects", []),
            key=lambda suspect: (suspect.score + self._proximity(suspect.reason, terms)),
            reverse=True,
        )
        return {**state, "suspects": ranked[: self.max_suspects]}

    @staticmethod
    def _proximity(reason: str, terms: list[str]) -> float:
        """Score reason text by overlap with bug-report terms."""
        reason_lower = reason.lower()
        return sum(0.1 for term in terms if len(term) > 3 and term in reason_lower)
