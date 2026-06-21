"""Agent service facade implementing the agent contract."""

from __future__ import annotations

from pathlib import Path
from typing import Any, cast

from ex04.services.agent.interface import AgentServiceInterface
from ex04.services.agent.state import AgentState
from ex04.services.agent.workflow import WorkflowBuilder
from ex04.shared.gatekeeper import GatekeeperInterface
from ex04.shared.types import InvestigationResult


class AgentService(AgentServiceInterface):
    """Run the LangGraph investigation workflow and expose its state."""

    def __init__(
        self,
        target_path: Path,
        max_iterations: int = 5,
        max_suspects: int = 5,
        context_limit: int = 8000,
        gatekeeper: GatekeeperInterface | None = None,
        provider: str = "openai",
    ) -> None:
        """Initialize the workflow service."""
        self._target_path = target_path
        self._builder = WorkflowBuilder(
            target_path=target_path,
            max_iterations=max_iterations,
            max_suspects=max_suspects,
            context_limit=context_limit,
            gatekeeper=gatekeeper,
            provider=provider,
        )
        self._state: AgentState = {}

    def investigate(
        self,
        bug_report: str,
        graph_path: Path | None = None,
        vault_path: Path | None = None,
    ) -> InvestigationResult:
        """Run a bug investigation and return a structured result."""
        state: AgentState = {"bug_report": bug_report, "iterations": 0}
        state["target_path"] = str(self._target_path)
        state["mode"] = "graph" if graph_path or vault_path else "naive"
        if graph_path:
            state["graph_context"] = str(graph_path)
        if vault_path:
            state["vault_context"] = str(vault_path)
        if state["mode"] == "naive":
            state["source_context"] = str(self._target_path)

        self._state = self._invoke_workflow(state)
        result = InvestigationResult(
            root_cause=self._state.get("root_cause", ""),
            suspects=self._state.get("suspects", []),
            proposed_fix=self._state.get("proposed_fix", ""),
            fix_applied=self._state.get("fix_applied", False),
            test_results=self._state.get("test_results", {}),
            original_problem=self._state.get("bug_report", ""),
            fix_diff=self._state.get("fix_diff", ""),
            files_read=self._state.get("files_read", 0),
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
        return cast(AgentState, dict(result))
