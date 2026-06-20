"""Deterministic Correctness Gate for candidate patches.

Validates a patch against the original failure without modifying the
pristine snapshot. All verification runs in a disposable working copy.
Captures stdout/stderr for failure-signature verification. AST-based
policy checks are delegated to gate_policies.

Traceability: [PRD-CE §Correctness Gate], [TODO P7-R01], [Correction #7]
"""

from __future__ import annotations

import shutil
import subprocess
import tempfile
from pathlib import Path

from ex04.services.comparison.gate_policies import (
    check_path_policy,
    check_test_dir_integrity,
    extract_changed_paths,
    snapshot_python_files,
)
from ex04.services.comparison.gate_report import write_gate_reports
from ex04.shared.types_experiment import GateOutput


class CorrectnessGate:
    """Validate a patch without touching the pristine snapshot.

    Steps: reproduce failure → check signature → apply patch →
    post-fix verification → path/AST policy checks → write reports.
    """

    def __init__(self, test_command: str = "python -m pytest", timeout: int = 60) -> None:
        """Initialize with test runner command and timeout in seconds."""
        self._cmd = test_command
        self._timeout = timeout

    def validate(  # noqa: PLR0913
        self, snapshot_path: Path, patch_diff: str, target_test: str = "",
        reproduction_command: str = "", expected_failure_signature: str = "",
        allowed_paths: list[str] | None = None,
        prohibited_paths: list[str] | None = None,
        suspected_files: list[str] | None = None,
        artifact_path: Path | None = None,
    ) -> GateOutput:
        """Run the full correctness gate against a candidate patch."""
        gate = GateOutput(evidence_class="deterministic_keyless_evidence")
        if not snapshot_path.exists():
            gate.limitations.append(f"Snapshot not found: {snapshot_path}")
            gate.final_verdict = "skipped"
            write_gate_reports(gate, artifact_path)
            return gate

        with tempfile.TemporaryDirectory() as tmp:
            disposable = Path(tmp) / "disposable"
            shutil.copytree(snapshot_path, disposable)
            pre = snapshot_python_files(disposable)

            repro = reproduction_command or self._cmd
            stdout, stderr, rc = self._capture(disposable, repro, target_test)
            gate.reproduction_stdout = stdout[:4096]
            gate.reproduction_stderr = stderr[:4096]
            gate.reproduction_rc = rc
            gate.failure_reproduced = rc != 0
            gate.failure_signature_found = (
                expected_failure_signature in (stdout + stderr)
                if expected_failure_signature else gate.failure_reproduced
            )

            if not patch_diff.strip():
                gate.limitations.append("No patch provided — skipping application.")
                gate.final_verdict = "skipped"
                write_gate_reports(gate, artifact_path)
                return gate

            gate.patch_applied = self._apply(disposable, patch_diff)
            if not gate.patch_applied:
                gate.limitations.append("Patch did not apply cleanly.")
                gate.final_verdict = "fail"
                write_gate_reports(gate, artifact_path)
                return gate

            _, _, gate.post_fix_rc = self._capture(disposable, repro, target_test)
            if target_test:
                _, _, trc = self._capture(disposable, self._cmd, target_test)
                gate.targeted_test_passed = trc == 0
            _, _, src = self._capture(disposable, self._cmd, "")
            gate.relevant_suite_passed = src == 0

            changed = extract_changed_paths(patch_diff)
            gate.path_violations = check_path_policy(
                changed, allowed_paths or [], prohibited_paths or []
            )
            gate.prohibited_files_clean = not gate.path_violations

            post = snapshot_python_files(disposable)
            ok_t, ok_a, iss = check_test_dir_integrity(pre, post)
            gate.tests_not_deleted, gate.assertions_not_weakened = ok_t, ok_a
            gate.limitations.extend(iss)

            if suspected_files and changed:
                gate.diagnosis_consistent = bool(set(suspected_files) & set(changed))

            gate.final_verdict = self._verdict(gate)

        write_gate_reports(gate, artifact_path)
        return gate

    def _capture(self, path: Path, cmd: str, tgt: str) -> tuple[str, str, int]:
        """Run command, capture stdout/stderr, return (stdout, stderr, rc)."""
        c = cmd.split() + ([tgt] if tgt else [])
        try:
            r = subprocess.run(c, cwd=path, capture_output=True, text=True,
                               timeout=self._timeout)
            return r.stdout, r.stderr, r.returncode
        except (subprocess.TimeoutExpired, FileNotFoundError):
            return "", "command not found or timed out", -1

    def _run_test(self, path: Path, test_target: str, expect_fail: bool = False) -> bool:
        """Run tests and return True on expected result (used by legacy tests)."""
        _, _, rc = self._capture(path, self._cmd, test_target)
        return rc != 0 if expect_fail else rc == 0

    def _apply(self, path: Path, diff: str) -> bool:
        """Apply a unified diff to the disposable copy."""
        try:
            r = subprocess.run(["patch", "-p1", "--batch"], input=diff, cwd=path,
                               capture_output=True, text=True, timeout=self._timeout)
            return r.returncode == 0
        except (subprocess.TimeoutExpired, FileNotFoundError):
            return False

    @staticmethod
    def _verdict(gate: GateOutput) -> str:
        """Compute final verdict from gate step results."""
        if not gate.failure_signature_found and gate.failure_reproduced:
            return "inconclusive"
        if gate.path_violations or not gate.tests_not_deleted or not gate.assertions_not_weakened:
            return "fail"
        if gate.targeted_test_passed is True and gate.relevant_suite_passed is True:
            return "pass"
        if gate.targeted_test_passed is False or gate.relevant_suite_passed is False:
            return "fail"
        return "partial"
