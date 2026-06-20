"""Regression tests for WorkflowBuilder target path wiring."""

from pathlib import Path
from unittest.mock import patch

from ex04.services.agent.nodes.inspect import CodeInspectionNode
from ex04.services.agent.workflow import WorkflowBuilder


def test_workflow_passes_target_path_to_inspection_node(tmp_path: Path) -> None:
    with patch("ex04.services.agent.workflow.StateGraph") as graph_cls:
        WorkflowBuilder(target_path=tmp_path).build()

    calls = graph_cls.return_value.add_node.call_args_list
    inspect_node = next(call.args[1] for call in calls if call.args[0] == "inspect")

    assert isinstance(inspect_node, CodeInspectionNode)
    assert inspect_node.target_path == tmp_path
