"""Basic tests for CodeInspectionNode — single/multiple suspects.

Tests that CodeInspectionNode reads source files for each suspect
location and formats them as structured text.

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

    Creates a directory structure with two Python files containing
    identifiable code for snippet extraction.

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


class TestCodeInspectionNodeBasic:
    """Tests for basic CodeInspectionNode functionality."""

    def test_inspects_single_suspect(self, node: CodeInspectionNode) -> None:
        """Test that a single suspect produces one code snippet."""
        state = {
            "suspects": [
                Suspect(
                    file_path=str(Path("src") / "main.py"),
                    line_start=1,
                    line_end=2,
                    score=0.9,
                    reason="Entry point",
                )
            ],
            "inspected_code": "",
        }
        result = node(state)
        assert "src/main.py" in result["inspected_code"]
        assert "def main():" in result["inspected_code"]

    def test_inspects_multiple_suspects(self, node: CodeInspectionNode) -> None:
        """Test that multiple suspects produce multiple code snippets."""
        state = {
            "suspects": [
                Suspect(
                    file_path=str(Path("src") / "main.py"),
                    line_start=1,
                    line_end=2,
                    score=0.9,
                ),
                Suspect(
                    file_path=str(Path("src") / "calc.py"),
                    line_start=4,
                    line_end=5,
                    score=0.7,
                ),
            ],
            "inspected_code": "",
        }
        result = node(state)
        assert "src/main.py" in result["inspected_code"]
        assert "src/calc.py" in result["inspected_code"]
