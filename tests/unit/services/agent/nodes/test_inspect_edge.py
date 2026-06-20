"""Edge case tests for CodeInspectionNode.

Tests graceful handling of missing files, invalid ranges, zero-based
line numbers, out-of-bounds line ends, and state preservation.

Implementation: **Phase 4** (T4.12)
"""

from __future__ import annotations

from pathlib import Path

import pytest

from ex04.services.agent.nodes.inspect import CodeInspectionNode
from ex04.shared.types_results import Suspect


@pytest.fixture
def temp_target(tmp_path: Path) -> Path:
    """Create a temporary target codebase with source files.

    Args:
        tmp_path: Pytest temporary directory fixture.

    Returns:
        Path to the temporary target codebase.
    """
    src = tmp_path / "src"
    src.mkdir()

    (src / "main.py").write_text(
        "def main():\n    print('Hello')\n    result = compute(1, 2)\n    print(result)\n",
        encoding="utf-8",
    )

    return tmp_path


@pytest.fixture
def node(temp_target: Path) -> CodeInspectionNode:
    """Create a CodeInspectionNode with a temporary target path.

    Args:
        temp_target: Temporary target codebase path.

    Returns:
        Configured CodeInspectionNode.
    """
    return CodeInspectionNode(target_path=temp_target)


class TestCodeInspectionNodeEdgeCases:
    """Tests for CodeInspectionNode edge case handling."""

    def test_empty_suspects_list(self, node: CodeInspectionNode) -> None:
        """Test that empty suspects produces empty inspected_code."""
        state = {"suspects": [], "inspected_code": ""}
        result = node(state)
        assert result["inspected_code"] == ""

    def test_missing_file_handled(self, node: CodeInspectionNode) -> None:
        """Test that missing files are skipped gracefully."""
        state = {
            "suspects": [
                Suspect(
                    file_path=str(Path("src") / "nonexistent.py"),
                    line_start=1,
                    line_end=5,
                )
            ],
            "inspected_code": "",
        }
        result = node(state)
        assert result["inspected_code"] == ""

    def test_invalid_line_range_handled(self, node: CodeInspectionNode) -> None:
        """Test that invalid line ranges (start > end) are handled."""
        state = {
            "suspects": [
                Suspect(
                    file_path=str(Path("src") / "main.py"),
                    line_start=10,
                    line_end=5,
                )
            ],
            "inspected_code": "",
        }
        result = node(state)
        assert result["inspected_code"] == ""

    def test_line_start_zero_handled(self, node: CodeInspectionNode) -> None:
        """Test that line_start of 0 is handled gracefully."""
        state = {
            "suspects": [
                Suspect(
                    file_path=str(Path("src") / "main.py"),
                    line_start=0,
                    line_end=2,
                )
            ],
            "inspected_code": "",
        }
        result = node(state)
        assert result["inspected_code"] == ""

    def test_line_end_exceeds_file_length(self, node: CodeInspectionNode) -> None:
        """Test that line_end beyond file length is clipped."""
        state = {
            "suspects": [
                Suspect(
                    file_path=str(Path("src") / "main.py"),
                    line_start=1,
                    line_end=100,
                )
            ],
            "inspected_code": "",
        }
        result = node(state)
        assert "def main():" in result["inspected_code"]

    def test_preserves_other_state_fields(self, node: CodeInspectionNode) -> None:
        """Test that other state fields are preserved."""
        state: dict = {
            "suspects": [],
            "inspected_code": "",
            "bug_report": "Test bug",
            "root_cause": "",
        }
        result = node(state)
        assert result["bug_report"] == "Test bug"
        assert result["root_cause"] == ""
