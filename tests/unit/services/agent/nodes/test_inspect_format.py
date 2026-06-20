"""Formatting tests for CodeInspectionNode — output structure.

Tests that snippets include file paths, line numbers, content, and
that multiple snippets are properly separated.

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

    (src / "calc.py").write_text(
        "def add(a, b):\n    return a + b\n\ndef compute(x, y):\n    return add(x, y) * 2\n",
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


class TestCodeInspectionNodeFormatting:
    """Tests for CodeInspectionNode output formatting."""

    def test_includes_file_path_header(self, node: CodeInspectionNode) -> None:
        """Test that each snippet includes its file path."""
        state = {
            "suspects": [
                Suspect(
                    file_path=str(Path("src") / "main.py"),
                    line_start=1,
                    line_end=1,
                )
            ],
            "inspected_code": "",
        }
        result = node(state)
        assert "src/main.py" in result["inspected_code"]

    def test_includes_line_numbers(self, temp_target: Path) -> None:
        """Test that snippets include line number markers."""
        node = CodeInspectionNode(target_path=temp_target)
        state = {
            "suspects": [
                Suspect(
                    file_path=str(Path("src") / "main.py"),
                    line_start=1,
                    line_end=1,
                )
            ],
            "inspected_code": "",
        }
        result = node(state)
        assert "1:" in result["inspected_code"] or "Line 1" in result["inspected_code"]

    def test_includes_code_content(self, node: CodeInspectionNode) -> None:
        """Test that snippets include the actual code content."""
        state = {
            "suspects": [
                Suspect(
                    file_path=str(Path("src") / "main.py"),
                    line_start=1,
                    line_end=1,
                )
            ],
            "inspected_code": "",
        }
        result = node(state)
        assert "def main():" in result["inspected_code"]

    def test_separates_multiple_snippets(self, node: CodeInspectionNode) -> None:
        """Test that multiple snippets are separated."""
        state = {
            "suspects": [
                Suspect(
                    file_path=str(Path("src") / "main.py"),
                    line_start=1,
                    line_end=1,
                ),
                Suspect(
                    file_path=str(Path("src") / "calc.py"),
                    line_start=1,
                    line_end=1,
                ),
            ],
            "inspected_code": "",
        }
        result = node(state)
        main_count = result["inspected_code"].count("src/main.py")
        calc_count = result["inspected_code"].count("src/calc.py")
        assert main_count >= 1
        assert calc_count >= 1
