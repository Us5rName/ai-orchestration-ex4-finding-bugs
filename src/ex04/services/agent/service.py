"""Agent service facade implementing the agent contract."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from ex04.services.agent.interface import AgentServiceInterface
from ex04.services.agent.state import AgentState
from ex04.services.agent.workflow import WorkflowBuilder
from ex04.shared.types import InvestigationResult


class AgentService(AgentServiceInterface):
    """Run the LangGraph investigation workflow and expose its state."""

    def __init__(self, target_path: Path, max_iterations: int = 5) -> None:
        """Initialize the workflow service."""
        self._target_path = target_path
        self._builder = WorkflowBuilder(target_path=target_path, max_iterations=max_iterations)
        self._state: AgentState = {}

    def investigate(
        self,
        bug_report: str,
        graph_path: Path | None = None,
        vault_path: Path | None = None,
    ) -> InvestigationResult:
        """Run a bug investigation and return a structured result."""
        state: AgentState = {"bug_report": bug_report, "iterations": 0}
        if graph_path:
            state["graph_context"] = str(graph_path)
        if vault_path:
            state["vault_context"] = str(vault_path)

        self._state = self._invoke_workflow(state)
        result = InvestigationResult(
            root_cause=self._state.get("root_cause", ""),
            suspects=self._state.get("suspects", []),
            proposed_fix=self._state.get("proposed_fix", ""),
            fix_applied=self._state.get("fix_applied", False),
            test_results=self._state.get("test_results", {}),
        )
        if "token_usage" in self._state:
            result.token_usage = self._state["token_usage"]
        return result

    def get_state(self) -> dict[str, Any]:
        """Return the latest workflow state."""
        return dict(self._state)

    def _invoke_workflow(self, state: AgentState) -> AgentState:
        """Invoke the compiled LangGraph workflow."""
        result = self._builder.build().invoke(state)
        return dict(result)
