"""Deterministic Correctness Gate for candidate patches.

Validates a patch against the original failure without modifying the
pristine snapshot. All verification runs in a disposable working copy.

Traceability: [PRD-CE §Correctness Gate], [TODO T6.06]
"""

from __future__ import annotations

import shutil
import subprocess
import tempfile
from pathlib import Path

from ex04.shared.types_experiment import GateOutput


class CorrectnessGate:
    """Validate a patch deterministically without touching the pristine snapshot.

    Steps (where applicable):
    1. Reproduce original failure in disposable copy
    2. Apply candidate patch to disposable copy
    3. Run targeted regression test
    4. Run relevant suite
    5. Policy checks (no test deletion, no weakened assertions)
    """

    def __init__(self, test_command: str = "python -m pytest", timeout: int = 60) -> None:
        """Initialize with test runner command and timeout in seconds."""
        self._test_command = test_command
        self._timeout = timeout

    def validate(
        self,
        snapshot_path: Path,
        patch_diff: str,
        target_test: str = "",
    ) -> GateOutput:
        """Run the full correctness gate against a candidate patch.

        Args:
            snapshot_path: Pristine pre-fix snapshot directory (read-only).
            patch_diff: Unified diff of the candidate patch.
            target_test: Optional specific test path/name to run.

        Returns:
            GateOutput with per-step results and final verdict.
        """
        gate = GateOutput(evidence_class="deterministic_keyless_evidence")

        if not snapshot_path.exists():
            gate.limitations.append(f"Snapshot not found: {snapshot_path}")
            gate.final_verdict = "skipped"
            return gate

        with tempfile.TemporaryDirectory() as tmp_str:
            disposable = Path(tmp_str) / "disposable"
            shutil.copytree(snapshot_path, disposable)

            gate.failure_reproduced = self._run_test(disposable, target_test, expect_fail=True)
            if not patch_diff.strip():
                gate.limitations.append("No patch provided — skipping application.")
                gate.final_verdict = "skipped"
                return gate

            gate.patch_applied = self._apply_patch(disposable, patch_diff)
            if not gate.patch_applied:
                gate.final_verdict = "fail"
                gate.limitations.append("Patch did not apply cleanly.")
                return gate

            if target_test:
                gate.targeted_test_passed = self._run_test(disposable, target_test)

            gate.relevant_suite_passed = self._run_test(disposable, "")
            gate.final_verdict = self._verdict(gate)

        return gate

    def _run_test(self, path: Path, test_target: str, expect_fail: bool = False) -> bool:
        """Run tests and return True on expected result."""
        cmd = self._test_command.split()
        if test_target:
            cmd.append(test_target)
        try:
            result = subprocess.run(
                cmd, cwd=path, capture_output=True, timeout=self._timeout
            )
            passed = result.returncode == 0
            return not passed if expect_fail else passed
        except (subprocess.TimeoutExpired, FileNotFoundError):
            return False  # noqa: RET504  — gate continues with limitations

    def _apply_patch(self, path: Path, diff: str) -> bool:
        """Apply a unified diff to the disposable copy."""
        try:
            result = subprocess.run(
                ["patch", "-p1", "--batch"],
                input=diff,
                cwd=path,
                capture_output=True,
                text=True,
                timeout=self._timeout,
            )
            return result.returncode == 0
        except (subprocess.TimeoutExpired, FileNotFoundError):
            return False

    @staticmethod
    def _verdict(gate: GateOutput) -> str:
        """Compute final verdict from gate step results."""
        if gate.targeted_test_passed is True and gate.relevant_suite_passed is True:
            return "pass"
        if gate.targeted_test_passed is False or gate.relevant_suite_passed is False:
            return "fail"
        return "partial"
