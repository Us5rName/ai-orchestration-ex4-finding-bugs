"""Tests for ComparisonCallService atomic call path."""

from __future__ import annotations

from unittest.mock import MagicMock

import pytest

from ex04.services.comparison.budget import BudgetLedger
from ex04.services.comparison.call_service import ComparisonCallService, InstrumentedCallResult
from ex04.services.comparison.trace import TraceRecorder
from ex04.shared.types_results import ProviderResponse


def _ledger() -> BudgetLedger:
    return BudgetLedger(
        max_files=10,
        max_bytes=100000,
        max_context_tokens=5000,
        max_tool_calls=20,
        max_model_calls=5,
        max_iterations=5,
        max_retries=0,
        timeout_seconds=60.0,
    )


def _gatekeeper(text: str = "ok", input_tokens: int = 10, output_tokens: int = 5) -> MagicMock:
    gk = MagicMock()
    resp = ProviderResponse(text=text, input_tokens=input_tokens, output_tokens=output_tokens)
    gk.send.return_value = resp
    return gk


def _trace() -> TraceRecorder:
    return TraceRecorder(run_id="test-run")


def test_execute_returns_instrumented_result() -> None:
    svc = ComparisonCallService(_gatekeeper())
    result = svc.execute([{"role": "user", "content": "hi"}], "openai", "gpt-4o", _ledger(), _trace())
    assert isinstance(result, InstrumentedCallResult)


def test_execute_delegates_to_gatekeeper() -> None:
    gk = _gatekeeper(text="hello")
    svc = ComparisonCallService(gk)
    result = svc.execute([{"role": "user", "content": "hi"}], "openai", "gpt-4o", _ledger(), _trace())
    gk.send.assert_called_once()
    assert result.response.text == "hello"


def test_execute_records_trace_event() -> None:
    trace = _trace()
    svc = ComparisonCallService(_gatekeeper())
    svc.execute([{"role": "user", "content": "hi"}], "openai", "gpt-4o", _ledger(), trace)
    assert any(e["operation"] == "provider_call" for e in trace.events)


def test_execute_updates_ledger_model_calls() -> None:
    ledger = _ledger()
    svc = ComparisonCallService(_gatekeeper())
    svc.execute([{"role": "user", "content": "hi"}], "openai", "gpt-4o", ledger, _trace())
    assert ledger.model_calls == 1


def test_execute_raises_on_gatekeeper_failure() -> None:
    gk = MagicMock()
    gk.send.side_effect = RuntimeError("provider down")
    svc = ComparisonCallService(gk)
    with pytest.raises(RuntimeError, match="provider down"):
        svc.execute([{"role": "user", "content": "hi"}], "openai", "gpt-4o", _ledger(), _trace())


def test_execute_raises_budget_exceeded_before_call() -> None:
    ledger = BudgetLedger(
        max_files=1, max_bytes=1, max_context_tokens=1,
        max_tool_calls=1, max_model_calls=0,  # 0 model calls allowed
        max_iterations=1, max_retries=0, timeout_seconds=60.0,
    )
    gk = _gatekeeper()
    svc = ComparisonCallService(gk)
    from ex04.services.comparison.budget import BudgetExceededError
    with pytest.raises(BudgetExceededError):
        svc.execute([{"role": "user", "content": "hi"}], "openai", "gpt-4o", ledger, _trace())
    # Gatekeeper must NOT have been called
    gk.send.assert_not_called()


def test_result_is_immutable() -> None:
    svc = ComparisonCallService(_gatekeeper())
    result = svc.execute([{"role": "user", "content": "hi"}], "openai", "gpt-4o", _ledger(), _trace())
    with pytest.raises(AttributeError):
        result.provider = "other"  # type: ignore[misc]


def test_both_modes_use_same_service_class() -> None:
    """NaiveRunner and GraphGuidedRunner must both hold a ComparisonCallService."""
    from ex04.services.comparison.graph_guided_runner import GraphGuidedRunner
    from ex04.services.comparison.naive_runner import NaiveRunner
    gk = _gatekeeper()
    naive = NaiveRunner(gk)
    graph = GraphGuidedRunner(gk)
    assert isinstance(naive._call_service, ComparisonCallService)
    assert isinstance(graph._call_service, ComparisonCallService)


def test_elapsed_seconds_is_non_negative() -> None:
    svc = ComparisonCallService(_gatekeeper())
    result = svc.execute([{"role": "user", "content": "hi"}], "openai", "gpt-4o", _ledger(), _trace())
    assert result.elapsed_seconds >= 0.0
