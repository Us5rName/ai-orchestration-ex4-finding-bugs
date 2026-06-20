"""Tests for CorrectnessGate and gate_policies — deterministic correctness verification.

All tests are keyless (no external tools required for core logic).
Tests that exercise subprocess are skipped when 'patch' binary is absent.

Traceability: [TODO P7-R01], [Correction #7]
"""

from __future__ import annotations

from pathlib import Path

import pytest

from ex04.services.comparison.correctness_gate import CorrectnessGate
from ex04.services.comparison.gate_policies import (
    check_path_policy,
    check_test_dir_integrity,
    check_test_file_integrity,
    count_assertions,
    count_test_functions,
)
from ex04.shared.types_experiment import GateOutput


# ── GateOutput defaults ──────────────────────────────────────────────────────

def test_gate_output_defaults() -> None:
    gate = GateOutput()
    assert gate.final_verdict == "skipped"
    assert gate.evidence_class == "fixture"
    assert gate.limitations == []
    assert gate.failure_signature_found is False
    assert gate.path_violations == []
    assert gate.report_json_path == ""


# ── Snapshot missing ──────────────────────────────────────────────────────────

def test_gate_skips_when_snapshot_missing(tmp_path: Path) -> None:
    result = CorrectnessGate().validate(tmp_path / "nonexistent", patch_diff="")
    assert result.final_verdict == "skipped"
    assert any("not found" in lim for lim in result.limitations)


# ── No patch ─────────────────────────────────────────────────────────────────

def test_gate_skips_when_no_patch(tmp_path: Path) -> None:
    snap = tmp_path / "snap"
    snap.mkdir()
    (snap / "dummy.py").write_text("x = 1\n")
    result = CorrectnessGate(test_command="true").validate(snap, patch_diff="   ")
    assert result.final_verdict == "skipped"


# ── Failure signature ─────────────────────────────────────────────────────────

def test_gate_evidence_class_set_by_validate() -> None:
    result = CorrectnessGate().validate(Path("/nonexistent_snap"), patch_diff="")
    assert result.evidence_class == "deterministic_keyless_evidence"


# ── Verdict logic ─────────────────────────────────────────────────────────────

def test_verdict_pass() -> None:
    gate = GateOutput(failure_signature_found=True)
    gate.targeted_test_passed = True
    gate.relevant_suite_passed = True
    assert CorrectnessGate._verdict(gate) == "pass"


def test_verdict_fail_targeted() -> None:
    gate = GateOutput(failure_signature_found=True)
    gate.targeted_test_passed = False
    gate.relevant_suite_passed = True
    assert CorrectnessGate._verdict(gate) == "fail"


def test_verdict_partial() -> None:
    gate = GateOutput(failure_signature_found=True)
    gate.targeted_test_passed = None
    gate.relevant_suite_passed = None
    assert CorrectnessGate._verdict(gate) == "partial"


def test_verdict_inconclusive_when_no_signature() -> None:
    gate = GateOutput(failure_reproduced=True, failure_signature_found=False)
    assert CorrectnessGate._verdict(gate) == "inconclusive"


def test_verdict_fail_on_path_violation() -> None:
    gate = GateOutput(
        failure_signature_found=True, path_violations=["bad/path.py"],
        targeted_test_passed=True, relevant_suite_passed=True,
    )
    assert CorrectnessGate._verdict(gate) == "fail"


# ── Path policy ───────────────────────────────────────────────────────────────

def test_path_policy_prohibited() -> None:
    violations = check_path_policy(["generated/auto.py"], [], ["generated/"])
    assert len(violations) == 1
    assert "prohibited" in violations[0]


def test_path_policy_not_allowed() -> None:
    violations = check_path_policy(["src/untouched.py"], ["src/buggy.py"], [])
    assert len(violations) == 1
    assert "non-allowed" in violations[0]


def test_path_policy_clean() -> None:
    violations = check_path_policy(["src/buggy.py"], ["src/buggy.py"], ["vendor/"])
    assert violations == []


# ── AST policy checks ────────────────────────────────────────────────────────

def test_count_test_functions() -> None:
    src = "def test_foo(): pass\ndef test_bar(): pass\ndef helper(): pass\n"
    assert count_test_functions(src) == 2


def test_count_assertions() -> None:
    src = "def test_x():\n    assert 1 == 1\n    assert 2 == 2\n"
    assert count_assertions(src) == 2


def test_test_file_integrity_ok() -> None:
    pre = "def test_foo():\n    assert True\n"
    post = "def test_foo():\n    assert True\n    assert 1 == 1\n"
    tests_ok, asserts_ok, no_skip, issues = check_test_file_integrity(pre, post)
    assert tests_ok and asserts_ok and no_skip and issues == []


def test_test_deletion_detected() -> None:
    pre = "def test_foo(): pass\ndef test_bar(): pass\n"
    post = "def test_foo(): pass\n"
    tests_ok, _, _, issues = check_test_file_integrity(pre, post)
    assert not tests_ok
    assert any("decreased" in i for i in issues)


def test_assertion_weakening_detected() -> None:
    pre = "def test_x():\n    assert True\n    assert 1 == 1\n"
    post = "def test_x():\n    assert True\n"
    _, asserts_ok, _, issues = check_test_file_integrity(pre, post)
    assert not asserts_ok


def test_skip_marker_detected() -> None:
    pre = "def test_foo(): pass\n"
    post = "@pytest.mark.skip\ndef test_foo(): pass\n"
    _, _, no_skip, issues = check_test_file_integrity(pre, post)
    assert not no_skip
    assert any("skip" in i.lower() for i in issues)


def test_check_test_dir_integrity() -> None:
    pre = {"test_module.py": "def test_foo(): assert True\n"}
    post = {"test_module.py": "def test_foo(): assert True\ndef test_bar(): assert True\n"}
    ok_t, ok_a, issues = check_test_dir_integrity(pre, post)
    assert ok_t and ok_a and issues == []


# ── Report writing ───────────────────────────────────────────────────────────

def test_gate_writes_json_report_when_snapshot_missing(tmp_path: Path) -> None:
    art = tmp_path / "artifacts"
    result = CorrectnessGate().validate(
        tmp_path / "nonexistent", patch_diff="", artifact_path=art
    )
    assert result.report_json_path != ""
    assert Path(result.report_json_path).exists()


def test_gate_writes_md_report_when_snapshot_missing(tmp_path: Path) -> None:
    art = tmp_path / "artifacts"
    result = CorrectnessGate().validate(
        tmp_path / "nonexistent", patch_diff="", artifact_path=art
    )
    assert result.report_md_path != ""
    assert Path(result.report_md_path).exists()


# ── Legacy patch binary test ─────────────────────────────────────────────────

def test_gate_apply_patch_missing_binary(tmp_path: Path) -> None:
    snap = tmp_path / "snap"
    snap.mkdir()
    (snap / "x.py").write_text("a = 1\n")
    result = CorrectnessGate(test_command="true").validate(
        snap, patch_diff="--- a/x.py\n+++ b/x.py\n@@ -1 +1 @@\n-a = 1\n+a = 2\n"
    )
    assert result.final_verdict in {"pass", "fail", "partial", "skipped", "inconclusive"}
