"""Mock Agent Service — canned investigation responses for testing."""

from __future__ import annotations

from dataclasses import asdict
from pathlib import Path

from ex04.services.agent.interface import AgentServiceInterface
from ex04.shared.types import InvestigationResult, Suspect, TokenMetrics


class MockAgentService(AgentServiceInterface):
    """Mock implementation of AgentServiceInterface with canned responses.

    Returns deterministic investigation results for testing without
    invoking LLM APIs or LangGraph workflows.
    """

    def investigate(
        self,
        bug_report: str,
        graph_path: Path | None = None,
        vault_path: Path | None = None,
    ) -> InvestigationResult:
        """Return a canned investigation result.

        Args:
            bug_report: Bug description (ignored in mock).
            graph_path: Optional graph path (ignored in mock).
            vault_path: Optional vault path (ignored in mock).

        Returns:
            InvestigationResult with synthetic root cause and suspects.
        """
        return InvestigationResult(
            root_cause="Null pointer in process_data() at line 15",
            suspects=[
                Suspect(
                    file_path="main.py",
                    line_start=15,
                    line_end=15,
                    score=0.9,
                    reason="Direct null access without guard",
                ),
            ],
            proposed_fix="Add None check before accessing the object",
            fix_applied=True,
            test_results={"passed": 10, "failed": 0},
            token_usage=TokenMetrics(
                input_tokens=500, output_tokens=200, total_tokens=700, provider="mock", model="mock"
            ),
        )

    def get_state(self) -> dict:
        """Return a mock agent state dict.

        Returns:
            Dict representing current LangGraph state.
        """
        return {
            "bug_report": "Test bug",
            "graph_context": "Test graph context",
            "vault_context": "Test vault context",
            "suspects": [],
            "root_cause": "",
            "proposed_fix": "",
            "fix_applied": False,
            "token_usage": asdict(TokenMetrics()),
        }
