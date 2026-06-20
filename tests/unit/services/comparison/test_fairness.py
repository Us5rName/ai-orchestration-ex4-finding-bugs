"""Tests for fairness contracts and runner structural invariants.

Verifies that controlled comparison fields are identical across modes,
FairnessEnforcer rejects mismatches before provider calls, and naive mode
cannot receive graph context while graph-guided mode can.

Traceability: [PRD-CE §Contracts and Fairness Invariants], [TODO T6.08]
"""

from __future__ import annotations

from pathlib import Path
from unittest.mock import MagicMock

import pytest

from ex04.services.comparison.fairness import FairnessEnforcer, FairnessViolationError
from ex04.services.comparison.graph_guided_runner import GraphGuidedRunner
from ex04.services.comparison.naive_runner import NaiveRunner
from ex04.shared.types import Entity, GraphData
from ex04.shared.types_experiment import ExperimentConfig
from ex04.shared.types_request import ComparisonRequest


def _base_req(**overrides: object) -> ComparisonRequest:
    defaults: dict[str, object] = {"bug_report": "test bug", "provider": "openai"}
    defaults.update(overrides)
    return ComparisonRequest(**defaults)  # type: ignore[arg-type]


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
    cfg = ExperimentConfig(bug_report="test bug", provider="openai", model="gpt-4o")
    assert cfg.provider == "openai"
    assert cfg.model == "gpt-4o"
    assert cfg.max_model_calls == 5
    assert cfg.max_tool_calls == 10
    assert cfg.max_iterations == 3
    assert cfg.token_budget == 8000
    assert cfg.prompt_version == "P6-CMP-01 v1.0"


def test_identical_requests_pass() -> None:
    """Two identical ComparisonRequest objects pass the fairness check."""
    enforcer = FairnessEnforcer()
    req = _base_req()
    enforcer.check(req, req)


@pytest.mark.parametrize(
    ("field", "naive_value", "guided_value"),
    [
        ("provider", "openai", "anthropic"),
        ("model", "gpt-4o-mini", "gpt-4o"),
        ("temperature", 0.0, 0.5),
        ("token_budget", 8000, 4000),
        ("max_files", 20, 10),
        ("system_prompt", "You are a debugger.", "You are a different debugger."),
    ],
)
def test_fairness_violation_on_controlled_fields(
    field: str, naive_value: object, guided_value: object
) -> None:
    """Different controlled field values raise FairnessViolationError."""
    enforcer = FairnessEnforcer()
    naive = _base_req(**{field: naive_value})
    guided = _base_req(**{field: guided_value})
    with pytest.raises(FairnessViolationError, match=field):
        enforcer.check(naive, guided)


def test_mode_specific_run_id_not_compared() -> None:
    """run_id is mode-specific and must not trigger a fairness violation."""
    enforcer = FairnessEnforcer()
    naive = _base_req(run_id="naive-001")
    guided = _base_req(run_id="guided-001")
    enforcer.check(naive, guided)


def test_config_hash_stable() -> None:
    """config_hash is deterministic for identical controlled fields."""
    req = _base_req()
    h1 = FairnessEnforcer.config_hash(req)
    h2 = FairnessEnforcer.config_hash(req)
    assert h1 == h2
    assert len(h1) == 64


def test_config_hash_differs_on_temperature() -> None:
    h1 = FairnessEnforcer.config_hash(_base_req(temperature=0.0))
    h2 = FairnessEnforcer.config_hash(_base_req(temperature=0.5))
    assert h1 != h2


def test_fairness_violation_before_send() -> None:
    """Enforcer must reject before gatekeeper.send() is called."""
    gk = _mock_gatekeeper()
    enforcer = FairnessEnforcer()
    with pytest.raises(FairnessViolationError):
        enforcer.check(_base_req(provider="openai"), _base_req(provider="anthropic"))
    gk.send.assert_not_called()


def test_naive_runner_does_not_accept_graph() -> None:
    """NaiveRunner.run signature does not accept graph_data."""
    import inspect

    sig = inspect.signature(NaiveRunner.run)
    assert "graph_data" not in sig.parameters
    assert "source_files" in sig.parameters


def test_graph_guided_runner_accepts_graph() -> None:
    """GraphGuidedRunner.run signature accepts graph_data."""
    import inspect

    sig = inspect.signature(GraphGuidedRunner.run)
    assert "graph_data" in sig.parameters


def test_naive_runner_reads_source_files(tmp_path: Path) -> None:
    """NaiveRunner reads from source_files, not graph data."""
    src = tmp_path / "module.py"
    src.write_text("def foo(): pass\n")
    gk = _mock_gatekeeper()
    result = NaiveRunner(gk, "openai").run("bug report", [src])
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
    GraphGuidedRunner(gk, "openai").run("bug", graph_data=graph, vault_path=None)
    call_args = gk.send.call_args[0][1]
    full_text = " ".join(str(m.get("content", "")) for m in call_args)
    assert "TargetClass" in full_text


def test_naive_runner_shared_provider() -> None:
    """NaiveRunner uses the same provider string it was initialized with."""
    runner = NaiveRunner(_mock_gatekeeper(), provider="anthropic")
    assert runner.provider == "anthropic"


def test_guided_runner_shared_provider() -> None:
    """GraphGuidedRunner uses the same provider string it was initialized with."""
    runner = GraphGuidedRunner(_mock_gatekeeper(), provider="anthropic")
    assert runner.provider == "anthropic"
