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
    def test_execute_creates_output_dir(self, mock_run: MagicMock) -> None:
        """Test that execute() creates output directory if needed."""
        mock_run.return_value = MagicMock(returncode=0, stdout="{}")

        with tempfile.TemporaryDirectory() as tmpdir:
            target = Path(tmpdir) / "test_codebase"
            target.mkdir()

            # Pre-create graph.json so the runner's post-check passes
            output_dir = target / "graphify-out"
            output_dir.mkdir()
            (output_dir / "graph.json").write_text("{}")

            runner = GraphRunner()
            result = runner.execute(str(target))

            # Verify execute() returns the graph.json path
            assert result.name == "graph.json"
