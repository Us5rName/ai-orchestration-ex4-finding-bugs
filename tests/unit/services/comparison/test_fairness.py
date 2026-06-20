"""Tests for comparison fairness invariants.

Verifies that both modes receive identical configuration, and that
naive mode does not use graph data while graph-guided mode does.

Traceability: [PRD-CE §Contracts and Fairness Invariants], [TODO T6.08]
"""

from __future__ import annotations

from pathlib import Path
from unittest.mock import MagicMock

from ex04.services.comparison.graph_guided_runner import GraphGuidedRunner
from ex04.services.comparison.naive_runner import NaiveRunner
from ex04.shared.types import Entity, GraphData
from ex04.shared.types_experiment import ExperimentConfig


def _mock_gatekeeper() -> MagicMock:
    gk = MagicMock()
    response = MagicMock()
    response.text = "diagnosis text"
    response.input_tokens = 100
    response.output_tokens = 50
    gk.send.return_value = response
    return gk


def test_experiment_config_shared_fields() -> None:
    """ExperimentConfig has all required fairness fields."""
    cfg = ExperimentConfig(
        bug_report="test bug",
        provider="openai",
        model="gpt-4o",
    )
    assert cfg.provider == "openai"
    assert cfg.model == "gpt-4o"
    assert cfg.max_model_calls == 5
    assert cfg.max_tool_calls == 10
    assert cfg.max_iterations == 3
    assert cfg.token_budget == 8000
    assert cfg.prompt_version == "P6-CMP-01 v1.0"


def test_naive_runner_does_not_use_graph() -> None:
    """NaiveRunner.run signature does not accept graph_data."""
    import inspect
    sig = inspect.signature(NaiveRunner.run)
    params = list(sig.parameters.keys())
    assert "graph_data" not in params
    assert "source_files" in params


def test_graph_guided_runner_uses_graph() -> None:
    """GraphGuidedRunner.run signature accepts graph_data."""
    import inspect
    sig = inspect.signature(GraphGuidedRunner.run)
    params = list(sig.parameters.keys())
    assert "graph_data" in params


def test_naive_runner_reads_source_files(tmp_path: Path) -> None:
    """NaiveRunner reads from source_files, not graph data."""
    src = tmp_path / "module.py"
    src.write_text("def foo(): pass\n")
    gk = _mock_gatekeeper()
    runner = NaiveRunner(gk, "openai")
    result = runner.run("bug report", [src])
    assert result.files_read == 1
    call_args = gk.send.call_args[0][1]
    assert any("foo" in str(m.get("content", "")) for m in call_args)


def test_graph_guided_runner_uses_entity_names() -> None:
    """GraphGuidedRunner uses entity names from graph_data in its prompt."""
    graph = GraphData(
        entities=[Entity(name="TargetClass", kind="class", file_path="x.py")],
        relationships=[],
    )
    gk = _mock_gatekeeper()
    runner = GraphGuidedRunner(gk, "openai")
    runner.run("bug", graph_data=graph, vault_path=None)
    call_args = gk.send.call_args[0][1]
    full_text = " ".join(str(m.get("content", "")) for m in call_args)
    assert "TargetClass" in full_text


def test_naive_runner_shared_provider(tmp_path: Path) -> None:
    """NaiveRunner uses the same provider string it was initialized with."""
    gk = _mock_gatekeeper()
    runner = NaiveRunner(gk, provider="anthropic")
    assert runner.provider == "anthropic"


def test_guided_runner_shared_provider() -> None:
    """GraphGuidedRunner uses the same provider string it was initialized with."""
    gk = _mock_gatekeeper()
    runner = GraphGuidedRunner(gk, provider="anthropic")
    assert runner.provider == "anthropic"
