"""Tests for ComparisonRequest contract."""

from __future__ import annotations

import pytest

from ex04.shared.types_request import ComparisonRequest


def test_default_construction() -> None:
    req = ComparisonRequest()
    assert req.max_files == 20
    assert req.max_bytes == 524288
    assert req.fixture_class == "fixture"


def test_validate_raises_on_empty_bug_report() -> None:
    req = ComparisonRequest(provider="openai", run_id="r1")
    with pytest.raises(ValueError, match="bug_report"):
        req.validate()


def test_validate_raises_on_empty_provider() -> None:
    req = ComparisonRequest(bug_report="test bug", run_id="r1")
    with pytest.raises(ValueError, match="provider"):
        req.validate()


def test_validate_raises_on_empty_run_id() -> None:
    req = ComparisonRequest(bug_report="test bug", provider="openai")
    with pytest.raises(ValueError, match="run_id"):
        req.validate()


def test_validate_raises_on_zero_budget() -> None:
    req = ComparisonRequest(bug_report="test bug", provider="openai", run_id="r1", max_files=0)
    with pytest.raises(ValueError, match="max_files"):
        req.validate()


def test_validate_raises_on_negative_budget() -> None:
    req = ComparisonRequest(
        bug_report="test bug", provider="openai", run_id="r1", token_budget=-1
    )
    with pytest.raises(ValueError, match="token_budget"):
        req.validate()


def test_validate_passes_on_valid_request() -> None:
    req = ComparisonRequest(bug_report="IndexError in process_data", provider="openai", run_id="r1")
    req.validate()  # must not raise


def test_default_gate_policy_checks() -> None:
    req = ComparisonRequest()
    assert "prohibited_files_clean" in req.gate_policy_checks
    assert "tests_not_deleted" in req.gate_policy_checks
    assert "assertions_not_weakened" in req.gate_policy_checks
