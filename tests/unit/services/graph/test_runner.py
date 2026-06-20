"""Tests for GraphRunner implementation (T4.01).

Tests GraphRunner.execute() against GraphServiceInterface contract:
- Invokes Grphify CLI via subprocess
- Returns path to generated graph.json
- Handles subprocess failures, missing Grphify, invalid target
- Logs execution output for debugging
"""

from __future__ import annotations

import tempfile
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

from ex04.services.graph.runner import GraphRunner


class TestGraphRunnerExecute:
    """Tests for GraphRunner.execute() method."""

    @patch("subprocess.run")
    def test_execute_calls_subprocess(self, mock_run: MagicMock) -> None:
        """Test that execute() calls subprocess to run Grphify."""
        mock_run.return_value = MagicMock(returncode=0, stdout="{}")

        with tempfile.TemporaryDirectory() as tmpdir:
            target = Path(tmpdir) / "test_codebase"
            target.mkdir()
            (target / "graphify-out").mkdir()
            (target / "graphify-out" / "graph.json").write_text("{}")

            runner = GraphRunner()
            result = runner.execute(str(target))

            mock_run.assert_called_once()
            assert isinstance(result, Path)

    @patch("subprocess.run")
    def test_execute_uses_extract_subcommand(self, mock_run: MagicMock) -> None:
        """execute() invokes ``graphify extract <path> --out <path>``."""
        mock_run.return_value = MagicMock(returncode=0, stdout="{}")

        with tempfile.TemporaryDirectory() as tmpdir:
            target = Path(tmpdir) / "test_codebase"
            target.mkdir()
            (target / "graphify-out").mkdir()
            (target / "graphify-out" / "graph.json").write_text("{}")

            GraphRunner().execute(str(target))

            cmd = mock_run.call_args.args[0]
            assert cmd[0] == "graphify"
            assert cmd[1] == "extract"
            assert str(target) in cmd
            assert "--out" in cmd
            # Output is read from <target>/graphify-out/, not a nested path.
            assert "--output" not in cmd

    @patch("subprocess.run")
    def test_execute_returns_graph_json_path(self, mock_run: MagicMock) -> None:
        """Test that execute() returns path to graph.json."""
        mock_run.return_value = MagicMock(returncode=0, stdout="{}")

        with tempfile.TemporaryDirectory() as tmpdir:
            target = Path(tmpdir) / "test_codebase"
            target.mkdir()
            (target / "graphify-out").mkdir()
            (target / "graphify-out" / "graph.json").write_text("{}")

            runner = GraphRunner()
            result = runner.execute(str(target))

            assert result.name == "graph.json"

    @patch("subprocess.run")
    def test_execute_handles_subprocess_failure(self, mock_run: MagicMock) -> None:
        """Test that execute() raises on non-zero return code."""
        mock_run.return_value = MagicMock(returncode=1, stderr="Grphify error")

        with tempfile.TemporaryDirectory() as tmpdir:
            target = Path(tmpdir) / "test_codebase"
            target.mkdir()
            (target / "graphify-out").mkdir()
            (target / "graphify-out" / "graph.json").write_text("{}")

            runner = GraphRunner()
            with pytest.raises(RuntimeError):
                runner.execute(str(target))

    def test_execute_handles_missing_target(self) -> None:
        """Test that execute() raises on non-existent target path."""
        runner = GraphRunner()
        with pytest.raises(FileNotFoundError):
            runner.execute("/nonexistent/path")

    @patch("subprocess.run")
    def test_execute_reads_graphify_out_location(self, mock_run: MagicMock) -> None:
        """execute() returns graph.json from <target>/graphify-out/."""
        mock_run.return_value = MagicMock(returncode=0, stdout="{}")

        with tempfile.TemporaryDirectory() as tmpdir:
            target = Path(tmpdir) / "test_codebase"
            target.mkdir()

            # Grphify writes here; simulate its output so the post-check passes.
            output_dir = target / "graphify-out"
            output_dir.mkdir()
            (output_dir / "graph.json").write_text("{}")

            result = GraphRunner().execute(str(target))

            assert result == output_dir / "graph.json"
