"""Agent Service Interface — contract for agent operations.

Defines the abstract base class that all agent service implementations
must follow. Enables parallel development — other modules depend only
on this interface, not on concrete implementations.

See ADR-005 for rationale.

Implementation: Phase 4 (T4.07–T4.15)
  - T4.07: AgentState (state.py)
  - T4.08: WorkflowBuilder (workflow.py)
  - T4.09: KnowledgeLoadNode (nodes/knowledge.py)
  - T4.10: BugAnalysisNode (nodes/analysis.py)
  - T4.11: SuspectRankingNode (nodes/suspect.py)
  - T4.12: CodeInspectionNode (nodes/inspect.py)
  - T4.13: RootCauseNode (nodes/rootcause.py)
  - T4.14: FixGenerationNode (nodes/fix.py)
  - T4.15: VerificationNode (nodes/verify.py)
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from pathlib import Path

from ex04.shared.types import InvestigationResult


class AgentServiceInterface(ABC):
    """Abstract interface for agent service operations.

    All agent-related operations (investigation, state management) must
    implement this interface. This enables dependency injection and
    mock-based testing.
    """

    @abstractmethod
    def investigate(
        self,
        bug_report: str,
        graph_path: Path | None = None,
        vault_path: Path | None = None,
    ) -> InvestigationResult:
        """Run a bug investigation using the agent workflow.

        Args:
            bug_report: Description of the bug to investigate.
            graph_path: Optional path to graph data for guided mode.
            vault_path: Optional path to vault for guided mode.

        Returns:
            InvestigationResult with root cause, suspects, and fix.
        """

    @abstractmethod
    def get_state(self) -> dict:
        """Get the current agent state.

        Returns:
            Dict representing the current LangGraph state.
        """
