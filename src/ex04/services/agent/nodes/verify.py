"""Verification Node — runs tests to confirm fix.

Executes tests on the fixed code and records results.
Determines whether to iterate or succeed.

Implementation: **Phase 4** (T4.15)
"""

from __future__ import annotations

import logging
import os
import subprocess
from pathlib import Path

from ex04.services.agent.state import AgentState

logger = logging.getLogger(__name__)


class VerificationNode:
    """Runs tests and determines success or retry.

    Executes the test suite on the fixed code and populates
    test_results in the state.

    Attributes:
        None — stateless node.
    """

    def __init__(self, command: list[str] | None = None, cwd: Path | str = ".") -> None:
        """Initialize with a verification command and working directory."""
        self.command = command or ["uv", "run", "pytest", "-q"]
        self.cwd = Path(cwd)

    def __call__(self, state: AgentState) -> AgentState:
        """Run verification tests and count the completed iteration.

        Incrementing ``iterations`` here lets the workflow's conditional edge
        bound the verify→suspect retry loop by ``max_iterations``.

        Args:
            state: Current agent state.

        Returns:
            State with test_results populated and the iteration counter bumped.
        """
        logger.info("VerificationNode: running tests")
        command: list[str] = state.get("test_command", self.command)
        cwd: os.PathLike[str] | str = state.get("test_cwd", self.cwd)
        completed = subprocess.run(
            command,
            cwd=cwd,
            capture_output=True,
            text=True,
            check=False,
        )
        failed = 0 if completed.returncode == 0 else 1
        results = {
            "command": command,
            "returncode": completed.returncode,
            "passed": completed.returncode == 0,
            "failed": failed,
            "stdout": completed.stdout,
            "stderr": completed.stderr,
        }
        return {**state, "test_results": results, "iterations": state.get("iterations", 0) + 1}
