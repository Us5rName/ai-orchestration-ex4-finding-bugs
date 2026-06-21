"""Edge case tests for CodeInspectionNode.

Tests graceful handling of missing files, invalid ranges, zero-based
line numbers, out-of-bounds line ends, and state preservation.

Implementation: **Phase 4** (T4.12)
"""

from __future__ import annotations

from collections.abc import Callable

from ex04.shared.types_results import Suspect


class TestCodeInspectionNodeEdgeCases:
    """Tests for CodeInspectionNode edge case handling."""

    def test_empty_suspects_list(self, node) -> None:
        """Test that empty suspects produces empty inspected_code."""
        state = {"suspects": [], "inspected_code": ""}
        result = node(state)
        assert result["inspected_code"] == ""

    def test_missing_file_handled(
        self,
        node,
        suspect: Callable[..., Suspect],
        inspect_state: Callable[..., dict],
    ) -> None:
        """Test that missing files are skipped gracefully."""
        state = inspect_state([suspect("src/nonexistent.py", start=1, end=5)])
        result = node(state)
        assert result["inspected_code"] == ""

    def test_invalid_line_range_handled(
        self,
        node,
        suspect: Callable[..., Suspect],
        inspect_state: Callable[..., dict],
    ) -> None:
        """Test that invalid line ranges (start > end) are handled."""
        state = inspect_state([suspect("src/main.py", start=10, end=5)])
        result = node(state)
        assert result["inspected_code"] == ""

    def test_line_start_zero_handled(
        self,
        node,
        suspect: Callable[..., Suspect],
        inspect_state: Callable[..., dict],
    ) -> None:
        """Test that line_start of 0 is handled gracefully."""
        state = inspect_state([suspect("src/main.py", start=0, end=2)])
        result = node(state)
        assert result["inspected_code"] == ""

    def test_line_end_exceeds_file_length(
        self,
        node,
        suspect: Callable[..., Suspect],
        inspect_state: Callable[..., dict],
    ) -> None:
        """Test that line_end beyond file length is clipped."""
        state = inspect_state([suspect("src/main.py", start=1, end=100)])
        result = node(state)
        assert "def main():" in result["inspected_code"]

    def test_preserves_other_state_fields(self, node) -> None:
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
