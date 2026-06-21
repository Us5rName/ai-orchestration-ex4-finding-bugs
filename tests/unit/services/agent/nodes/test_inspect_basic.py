"""Basic tests for CodeInspectionNode — single/multiple suspects.

Tests that CodeInspectionNode reads source files for each suspect
location and formats them as structured text.

Implementation: **Phase 4** (T4.12)
"""

from __future__ import annotations

from collections.abc import Callable

from ex04.shared.types_results import Suspect


class TestCodeInspectionNodeBasic:
    """Tests for basic CodeInspectionNode functionality."""

    def test_inspects_single_suspect(
        self,
        node,
        suspect: Callable[..., Suspect],
        inspect_state: Callable[..., dict],
    ) -> None:
        """Test that a single suspect produces one code snippet."""
        state = inspect_state([suspect("src/main.py", reason="Entry point")])
        result = node(state)
        assert "src/main.py" in result["inspected_code"]
        assert "def main():" in result["inspected_code"]

    def test_inspects_multiple_suspects(
        self,
        node,
        suspect: Callable[..., Suspect],
        inspect_state: Callable[..., dict],
    ) -> None:
        """Test that multiple suspects produce multiple code snippets."""
        state = inspect_state([
            suspect("src/main.py", start=1, end=2),
            suspect("src/calc.py", start=4, end=5, score=0.7),
        ])
        result = node(state)
        assert "src/main.py" in result["inspected_code"]
        assert "src/calc.py" in result["inspected_code"]
