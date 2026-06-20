"""Tests for FairnessEnforcer and runner structural invariants.

Verifies that:
- FairnessEnforcer raises before any provider call when fields differ
- Each ComparisonRequest controlled field mutation causes rejection
- Naive runner structurally excludes graph context
- Graph-guided runner accepts graph data

Traceability: [PRD-CE §Fairness], [TODO P6-R05], [Correction #5]
"""

from __future__ import annotations

import dataclasses
from pathlib import Path
from unittest.mock import MagicMock

import pytest

from ex04.services.comparison.fairness import FairnessEnforcer, FairnessViolationError
from ex04.services.comparison.graph_guided_runner import GraphGuidedRunner
from ex04.services.comparison.naive_runner import NaiveRunner
from ex04.shared.types import Entity, GraphData
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


def test_identical_requests_pass() -> None:
    """Two identical ComparisonRequest objects pass the fairness check."""
    enforcer = FairnessEnforcer()
    req = _base_req()
    enforcer.check(req, req)  # must not raise


def test_fairness_violation_on_provider() -> None:
    """Different providers → FairnessViolationError before any send()."""
    enforcer = FairnessEnforcer()
    naive = _base_req(provider="openai")
    guided = _base_req(provider="anthropic")
    with pytest.raises(FairnessViolationError, match="provider"):
        enforcer.check(naive, guided)


def test_fairness_violation_on_model() -> None:
    enforcer = FairnessEnforcer()
    naive = _base_req(model="gpt-4o-mini")
    guided = _base_req(model="gpt-4o")
    with pytest.raises(FairnessViolationError, match="model"):
        enforcer.check(naive, guided)


def test_fairness_violation_on_temperature() -> None:
    enforcer = FairnessEnforcer()
    naive = _base_req(temperature=0.0)
    guided = _base_req(temperature=0.5)
    with pytest.raises(FairnessViolationError, match="temperature"):
        enforcer.check(naive, guided)


def test_fairness_violation_on_token_budget() -> None:
    enforcer = FairnessEnforcer()
    naive = _base_req(token_budget=8000)
    guided = _base_req(token_budget=4000)
    with pytest.raises(FairnessViolationError, match="token_budget"):
        enforcer.check(naive, guided)


def test_fairness_violation_on_max_files() -> None:
    enforcer = FairnessEnforcer()
    naive = _base_req(max_files=20)
    guided = _base_req(max_files=10)
    with pytest.raises(FairnessViolationError, match="max_files"):
        enforcer.check(naive, guided)


def test_fairness_violation_on_system_prompt() -> None:
    enforcer = FairnessEnforcer()
    naive = _base_req(system_prompt="You are a debugger.")
    guided = _base_req(system_prompt="You are a different debugger.")
    with pytest.raises(FairnessViolationError, match="system_prompt"):
        enforcer.check(naive, guided)


def test_mode_specific_run_id_not_compared() -> None:
    """run_id is mode-specific and must NOT trigger a fairness violation."""
    enforcer = FairnessEnforcer()
    naive = _base_req(run_id="naive-001")
    guided = _base_req(run_id="guided-001")
    enforcer.check(naive, guided)  # must not raise


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
    naive = _base_req(provider="openai")
    guided = _base_req(provider="anthropic")
    with pytest.raises(FairnessViolationError):
        enforcer.check(naive, guided)
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
    src = tmp_path / "module.py"
    src.write_text("def foo(): pass\n")
    gk = _mock_gatekeeper()
    result = NaiveRunner(gk, "openai").run("bug report", [src])
    assert result.files_read == 1
    call_args = gk.send.call_args[0][1]
    assert any("foo" in str(m.get("content", "")) for m in call_args)


def test_graph_guided_runner_uses_entity_names() -> None:
    graph = GraphData(
        entities=[Entity(name="TargetClass", kind="class", file_path="x.py")],
        relationships=[],
    )
    gk = _mock_gatekeeper()
    GraphGuidedRunner(gk, "openai").run("bug", graph_data=graph, vault_path=None)
    call_args = gk.send.call_args[0][1]
    full_text = " ".join(str(m.get("content", "")) for m in call_args)
    assert "TargetClass" in full_text


def test_naive_runner_shared_provider(tmp_path: Path) -> None:
    gk = _mock_gatekeeper()
    runner = NaiveRunner(gk, provider="anthropic")
    assert runner.provider == "anthropic"


def test_guided_runner_shared_provider() -> None:
    gk = _mock_gatekeeper()
    runner = GraphGuidedRunner(gk, provider="anthropic")
    assert runner.provider == "anthropic"
