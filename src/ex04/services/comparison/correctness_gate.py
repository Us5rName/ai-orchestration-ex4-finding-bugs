"""Deterministic correctness gate for candidate patches."""

from __future__ import annotations

import hashlib
import shlex
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
    """Validate a patch in a disposable copy of the target snapshot."""

    def __init__(self, test_command: str = "python -m pytest", timeout: int = 60) -> None:
        self._cmd = test_command
        self._timeout = timeout

    def validate(  # noqa: PLR0913
        self, snapshot_path: Path, patch_diff: str, target_test: str = "",
        reproduction_command: str = "", expected_failure_signature: str = "",
        allowed_paths: list[str] | None = None,
        prohibited_paths: list[str] | None = None,
        suspected_files: list[str] | None = None,
        artifact_path: Path | None = None,
        verification_commands: list[str] | None = None,
    ) -> GateOutput:
        """Run reproduce, patch, post-fix, verification, and policy checks."""
        gate = GateOutput(evidence_class="deterministic")
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
            out, err, rc = self._capture(disposable, repro, target_test)
            gate.reproduction_stdout, gate.reproduction_stderr = out[:4096], err[:4096]
            gate.reproduction_rc = rc
            gate.failure_reproduced = rc != 0
            gate.failure_signature_found = bool(
                expected_failure_signature and expected_failure_signature in (out + err)
            )
            if not patch_diff.strip():
                gate.limitations.append("No patch provided; skipping application.")
                gate.final_verdict = "skipped"
                write_gate_reports(gate, artifact_path)
                return gate
            gate.patch_hash = hashlib.sha256(patch_diff.encode()).hexdigest()
            gate.patch_applied = self._apply(disposable, patch_diff)
            if gate.patch_applied:
                self._post_patch_checks(
                    gate, disposable, repro, target_test, verification_commands or []
                )
                self._policy_checks(
                    gate, patch_diff, pre, disposable, allowed_paths or [],
                    prohibited_paths or [], suspected_files or [],
                )
            else:
                gate.limitations.append("Patch did not apply cleanly.")
            gate.final_verdict = self._verdict(gate, bool(expected_failure_signature))
        write_gate_reports(gate, artifact_path)
        return gate

    def _post_patch_checks(
        self, gate: GateOutput, path: Path, repro: str, target: str,
        verification_commands: list[str],
    ) -> None:
        out, err, gate.post_fix_rc = self._capture(path, repro, target)
        gate.post_fix_stdout, gate.post_fix_stderr = out[:4096], err[:4096]
        if target:
            _, _, trc = self._capture(path, self._cmd, target)
            gate.targeted_test_passed = trc == 0
        _, _, src = self._capture(path, self._cmd, "")
        gate.relevant_suite_passed = src == 0
        for cmd in verification_commands:
            stdout, stderr, rc = self._capture(path, cmd, "")
            gate.verification_results.append({
                "argv": shlex.split(cmd), "exit_code": rc,
                "stdout": stdout[:4096], "stderr": stderr[:4096],
            })

    def _policy_checks(
        self, gate: GateOutput, diff: str, pre: dict[str, str], path: Path,
        allowed: list[str], prohibited: list[str], suspected: list[str],
    ) -> None:
        changed = extract_changed_paths(diff)
        gate.path_violations = check_path_policy(changed, allowed, prohibited)
        gate.prohibited_files_clean = not gate.path_violations
        ok_t, ok_a, issues = check_test_dir_integrity(pre, snapshot_python_files(path))
        gate.tests_not_deleted, gate.assertions_not_weakened = ok_t, ok_a
        gate.limitations.extend(issues)
        gate.diagnosis_consistent = bool(set(suspected) & set(changed)) if suspected else True

    def _capture(self, path: Path, cmd: str, tgt: str) -> tuple[str, str, int]:
        argv = shlex.split(cmd) + ([tgt] if tgt else [])
        try:
            r = subprocess.run(argv, cwd=path, capture_output=True, text=True,
                               timeout=self._timeout)
            return r.stdout, r.stderr, r.returncode
        except (subprocess.TimeoutExpired, FileNotFoundError) as exc:
            return "", str(exc), -1

    def _run_test(self, path: Path, test_target: str, expect_fail: bool = False) -> bool:
        """Legacy helper used by tests."""
        _, _, rc = self._capture(path, self._cmd, test_target)
        return rc != 0 if expect_fail else rc == 0

    def _apply(self, path: Path, diff: str) -> bool:
        try:
            r = subprocess.run(["patch", "-p1", "--batch"], input=diff, cwd=path,
                               capture_output=True, text=True, timeout=self._timeout)
            return r.returncode == 0
        except (subprocess.TimeoutExpired, FileNotFoundError):
            return False

    @staticmethod
    def _verdict(gate: GateOutput, require_signature: bool = True) -> str:
        """Compute mandatory final verdict."""
        if not gate.failure_reproduced:
            return "fail"
        if require_signature and not gate.failure_signature_found:
            return "inconclusive"
        if not gate.patch_applied or gate.post_fix_rc != 0:
            return "fail"
        if gate.path_violations or not gate.tests_not_deleted or not gate.assertions_not_weakened:
            return "fail"
        if gate.targeted_test_passed is False or gate.relevant_suite_passed is False:
            return "fail"
        if any(item.get("exit_code") != 0 for item in gate.verification_results):
            return "fail"
        return "pass"
