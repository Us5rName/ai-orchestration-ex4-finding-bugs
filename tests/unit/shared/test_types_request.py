"""Tests for ComparisonRequest contract."""

from __future__ import annotations

import pytest

from ex04.shared.types_request import (
    CONTROLLED,
    FAIRNESS_CLASSES,
    ComparisonRequest,
    classified_field_names,
    fairness_of,
)


def test_default_construction() -> None:
    req = ComparisonRequest()
    assert req.max_files == 20
    assert req.max_bytes == 524288
    assert req.fixture_class == "fixture"
    assert req.evidence_class == "fixture"


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
    req = ComparisonRequest(
        bug_report="test bug",
        provider="openai",
        run_id="r1",
        max_files=0,
    )
    with pytest.raises(ValueError, match="max_files"):
        req.validate()


def test_validate_raises_on_negative_budget() -> None:
    req = ComparisonRequest(
        bug_report="test bug",
        provider="openai",
        run_id="r1",
        token_budget=-1,
    )
    with pytest.raises(ValueError, match="token_budget"):
        req.validate()


def test_validate_passes_on_valid_request() -> None:
    req = ComparisonRequest(
        bug_report="IndexError in process_data",
        provider="openai",
        run_id="r1",
    )
    req.validate()


def test_default_gate_policy_checks() -> None:
    req = ComparisonRequest()
    assert "prohibited_files_clean" in req.gate_policy_checks
    assert "tests_not_deleted" in req.gate_policy_checks
    assert "assertions_not_weakened" in req.gate_policy_checks


def test_every_field_has_fairness_classification() -> None:
    names = set(ComparisonRequest.__dataclass_fields__)
    classified = {
        name for kind in FAIRNESS_CLASSES for name in classified_field_names(kind)
    }
    assert classified == names


def test_invalid_target_identity_rejected_for_non_fixture() -> None:
    req = ComparisonRequest(
        bug_report="bug",
        provider="openai",
        run_id="r1",
        evidence_class="deterministic",
    )
    with pytest.raises(ValueError, match="target_commit"):
        req.validate()


def test_invalid_evidence_class_rejected() -> None:
    req = ComparisonRequest(
        bug_report="bug",
        provider="openai",
        run_id="r1",
        evidence_class="demo",
    )
    with pytest.raises(ValueError, match="evidence_class"):
        req.validate()


def test_controlled_hash_is_full_sha256() -> None:
    req = ComparisonRequest(bug_report="bug", provider="openai", run_id="naive")
    digest = req.controlled_config_hash()
    assert len(digest) == 64
    assert all(ch in "0123456789abcdef" for ch in digest)
    assert digest != req.fixture_class


def test_mode_fields_do_not_change_controlled_hash() -> None:
    base = ComparisonRequest(bug_report="bug", provider="openai", run_id="naive")
    guided = ComparisonRequest(
        bug_report="bug",
        provider="openai",
        run_id="guided",
        mode="graph",
    )
    assert base.controlled_config_hash() == guided.controlled_config_hash()


def test_controlled_payload_contains_only_controlled_fields() -> None:
    req = ComparisonRequest(bug_report="bug", provider="openai", run_id="naive")
    assert set(req.controlled_payload()) == set(classified_field_names(CONTROLLED))
    assert fairness_of("run_id") != CONTROLLED
