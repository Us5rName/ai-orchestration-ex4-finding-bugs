"""Graph Runner — executes Grphify CLI to build code graphs.

Runs Grphify as an external CLI tool via subprocess to extract code
structure from a target codebase. Returns the path to the generated
graph.json output file.

Implementation: Phase 4 (T4.01)
"""

from __future__ import annotations

import logging
import subprocess
from pathlib import Path

logger = logging.getLogger(__name__)


class GraphRunner:
    """Execute Grphify CLI on a target codebase.

    Runs the Grphify CLI tool via subprocess to build a code graph.
    Creates the output directory if needed and returns the path to
    the generated graph.json file.

    Attributes:
        command: The Grphify CLI command to execute.
    """

    def __init__(self, command: str = "graphify") -> None:
        """Initialize with Grphify CLI command.

        Args:
            command: Path to or name of the Grphify CLI executable.
        """
        self.command = command

    def execute(self, target_path: str) -> Path:
        """Run Grphify on a target codebase and return graph.json path.

        Args:
            target_path: Path to the target codebase directory.

        Returns:
            Path to the generated graph.json output file.

        Raises:
            FileNotFoundError: If the target path does not exist.
            RuntimeError: If Grphify execution fails.
        """
        target = Path(target_path)
        if not target.exists():
            raise FileNotFoundError(f"Target codebase not found: {target_path}")

        output_dir = target / "graphify-out"
        output_dir.mkdir(parents=True, exist_ok=True)

        cmd = [self.command, target_path, "--output", str(output_dir)]
        logger.info("Running Grphify: %s", " ".join(cmd))

        result = subprocess.run(cmd, capture_output=True, text=True, timeout=300)

        if result.returncode != 0:
            logger.error("Grphify failed: %s", result.stderr)
            raise RuntimeError(f"Grphify failed (exit {result.returncode}): {result.stderr}")

        graph_file = output_dir / "graph.json"
        if not graph_file.exists():
            raise RuntimeError(f"Grphify did not produce graph.json at {graph_file}")

        logger.info("Graph generated at %s", graph_file)
        return graph_file
