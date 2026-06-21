"""Tests for CorrectnessGate — deterministic correctness verification.

All tests are keyless (no external tools required for core logic).
Tests that exercise subprocess are skipped when 'patch' binary is absent.
"""

from __future__ import annotations

from pathlib import Path

from ex04.services.comparison.correctness_gate import CorrectnessGate
from ex04.shared.types_experiment import GateOutput


def test_gate_output_defaults() -> None:
    """GateOutput defaults represent a skipped/safe state."""
    gate = GateOutput()
    assert gate.final_verdict == "skipped"
    assert gate.evidence_class == "fixture"
    assert gate.limitations == []


def test_gate_skips_when_snapshot_missing(tmp_path: Path) -> None:
    """Gate returns skipped verdict when snapshot does not exist."""
    cg = CorrectnessGate()
    result = cg.validate(tmp_path / "nonexistent", patch_diff="")
    assert result.final_verdict == "skipped"
    assert any("not found" in lim for lim in result.limitations)


def test_gate_skips_when_no_patch(tmp_path: Path) -> None:
    """Gate skips when empty patch provided (nothing to apply)."""
    snapshot = tmp_path / "snapshot"
    snapshot.mkdir()
    (snapshot / "dummy.py").write_text("x = 1\n")
    cg = CorrectnessGate(test_command="true")
    result = cg.validate(snapshot, patch_diff="   ")
    assert result.final_verdict == "skipped"


def test_gate_evidence_class_set_by_validate() -> None:
    """validate() sets evidence_class to deterministic_keyless_evidence."""
    snapshot = Path("/nonexistent_snapshot_xyz")
    cg = CorrectnessGate()
    result = cg.validate(snapshot, patch_diff="")
    assert result.evidence_class == "deterministic_keyless_evidence"


def test_verdict_logic_pass() -> None:
    """Verdict is pass when both targeted test and suite pass."""
    gate = GateOutput()
    gate.targeted_test_passed = True
    gate.relevant_suite_passed = True
    verdict = CorrectnessGate._verdict(gate)
    assert verdict == "pass"


def test_verdict_logic_fail_targeted() -> None:
    """Verdict is fail when targeted test fails."""
    gate = GateOutput()
    gate.targeted_test_passed = False
    gate.relevant_suite_passed = True
    assert CorrectnessGate._verdict(gate) == "fail"


def test_verdict_logic_partial() -> None:
    """Verdict is partial when targeted test not run but suite not failing."""
    gate = GateOutput()
    gate.targeted_test_passed = None
    gate.relevant_suite_passed = None
    assert CorrectnessGate._verdict(gate) == "partial"


def test_gate_apply_patch_missing_binary(tmp_path: Path) -> None:
    """Gate handles missing 'patch' binary gracefully."""
    snapshot = tmp_path / "snap"
    snapshot.mkdir()
    (snapshot / "x.py").write_text("a = 1\n")
    cg = CorrectnessGate(test_command="true")
    result = cg.validate(snapshot, patch_diff="--- a/x.py\n+++ b/x.py\n@@ -1 +1 @@\n-a = 1\n+a = 2\n")
    # Either applied or not — important that it doesn't crash
    assert result.final_verdict in {"pass", "fail", "partial", "skipped"}
