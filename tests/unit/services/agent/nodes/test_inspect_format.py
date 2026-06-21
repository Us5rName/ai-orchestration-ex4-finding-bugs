"""Formatting tests for CodeInspectionNode — output structure.

Tests that snippets include file paths, line numbers, content, and
that multiple snippets are properly separated.

Implementation: **Phase 4** (T4.12)
"""

from __future__ import annotations

from collections.abc import Callable

from ex04.shared.types_results import Suspect


class TestCodeInspectionNodeFormatting:
    """Tests for CodeInspectionNode output formatting."""

    def test_includes_file_path_header(
        self,
        node,
        suspect: Callable[..., Suspect],
        inspect_state: Callable[..., dict],
    ) -> None:
        """Test that each snippet includes its file path."""
        state = inspect_state([suspect("src/main.py", start=1, end=1)])
        result = node(state)
        assert "src/main.py" in result["inspected_code"]

    def test_includes_line_numbers(
        self,
        node,
        suspect: Callable[..., Suspect],
        inspect_state: Callable[..., dict],
    ) -> None:
        """Test that snippets include line number markers."""
        state = inspect_state([suspect("src/main.py", start=1, end=1)])
        result = node(state)
        assert "1:" in result["inspected_code"] or "Line 1" in result["inspected_code"]

    def test_includes_code_content(
        self,
        node,
        suspect: Callable[..., Suspect],
        inspect_state: Callable[..., dict],
    ) -> None:
        """Test that snippets include the actual code content."""
        state = inspect_state([suspect("src/main.py", start=1, end=1)])
        result = node(state)
        assert "def main():" in result["inspected_code"]

    def test_separates_multiple_snippets(
        self,
        node,
        suspect: Callable[..., Suspect],
        inspect_state: Callable[..., dict],
    ) -> None:
        """Test that multiple snippets are separated."""
        state = inspect_state([
            suspect("src/main.py", start=1, end=1),
            suspect("src/calc.py", start=1, end=1),
        ])
        result = node(state)
        main_count = result["inspected_code"].count("src/main.py")
        calc_count = result["inspected_code"].count("src/calc.py")
        assert main_count >= 1
        assert calc_count >= 1
