"""Tests for AgentService facade."""

from pathlib import Path

from ex04.services.agent.service import AgentService
from ex04.shared.types import Suspect


class _Workflow:
    def invoke(self, state: dict) -> dict:
        return {
            **state,
            "root_cause": "bad branch",
            "suspects": [Suspect("app.py", 1, 2)],
            "proposed_fix": "change condition",
            "fix_applied": False,
            "test_results": {"failed": 1},
            "files_read": 3,
        }


def test_agent_service_maps_workflow_state_to_result(tmp_path: Path) -> None:
    service = AgentService(tmp_path)
    service._builder.build = lambda: _Workflow()  # type: ignore[method-assign]

    result = service.investigate("crash", Path("graph.json"), Path("vault"))

    assert result.root_cause == "bad branch"
    assert result.suspects[0].file_path == "app.py"
    assert result.files_read == 3
    assert service.get_state()["graph_context"] == "graph.json"
