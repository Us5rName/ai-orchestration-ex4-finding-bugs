"""Tests for shared comparison budget and trace infrastructure."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from ex04.services.comparison.budget import (
    BudgetExceededError,
    BudgetLedger,
    estimate_context_tokens,
)
from ex04.services.comparison.trace import TraceRecorder
from ex04.shared.types_request import ComparisonRequest


def _ledger() -> BudgetLedger:
    req = ComparisonRequest(
        bug_report="bug", provider="openai", run_id="r1",
        max_files=2, max_bytes=20, token_budget=10, max_tool_calls=3,
        max_model_calls=1, max_iterations=2, max_retries=1,
    )
    return BudgetLedger.from_request(req)


def test_token_estimator_is_deterministic() -> None:
    assert estimate_context_tokens("abcd") == 1
    assert estimate_context_tokens("abcde") == 2
    assert estimate_context_tokens("") == 0


def test_budget_checked_before_recording() -> None:
    ledger = _ledger()
    ledger.check(files=1, bytes_=10, tokens=3, tools=1)
    ledger.record(files=1, bytes_=10, tokens=3, tools=1)
    with pytest.raises(BudgetExceededError, match="files_read"):
        ledger.check(files=2)
    assert ledger.files_read == 1


def test_retry_counters_remain_cumulative() -> None:
    ledger = _ledger()
    ledger.record(retries=1, tools=1)
    with pytest.raises(BudgetExceededError, match="retries"):
        ledger.check(retries=1)
    assert ledger.retries == 1
    assert ledger.tool_calls == 1


def test_model_call_budget_prevents_provider_call() -> None:
    ledger = _ledger()
    ledger.check(models=1)
    ledger.record(models=1)
    with pytest.raises(BudgetExceededError, match="model_calls"):
        ledger.check(models=1)


def test_trace_records_actual_counters_and_hash(tmp_path: Path) -> None:
    ledger = _ledger()
    trace = TraceRecorder("run-a")
    ledger.record(files=1, bytes_=8, tokens=2, tools=1)
    trace.record("read_file", ledger, path="src/example.py", bytes=8)
    path, digest = trace.persist(tmp_path)

    lines = path.read_text(encoding="utf-8").splitlines()
    event = json.loads(lines[0])
    assert event["sequence"] == 1
    assert event["operation"] == "read_file"
    assert event["files_read"] == 1
    assert event["tool_calls"] == 1
    assert len(digest) == 64


def test_trace_persist_rejects_overwrite(tmp_path: Path) -> None:
    ledger = _ledger()
    trace = TraceRecorder("run-a")
    trace.record("tree_list", ledger)
    trace.persist(tmp_path)
    with pytest.raises(FileExistsError):
        trace.persist(tmp_path)
