"""Tests for cumulative files_read accounting in CodeInspectionNode.

Verifies that files_read accumulates across retry cycles rather than
being reset on each inspection pass.

Implementation: Phase 4 (T4.12)
"""

from __future__ import annotations

from collections.abc import Callable

from ex04.shared.types_results import Suspect


class TestFilesReadCumulative:
    """Cumulative files_read behavior across inspection passes."""

    def test_initial_state_no_files_read_key(self, node, suspect: Callable[..., Suspect]) -> None:
        """First pass with no existing files_read key starts from zero."""
        state = {"suspects": [suspect("src/main.py")]}
        result = node(state)
        assert result["files_read"] == 1

    def test_existing_nonzero_count_is_preserved(
        self,
        node,
        suspect: Callable[..., Suspect],
    ) -> None:
        """Existing nonzero files_read is incremented, not overwritten."""
        state = {"suspects": [suspect("src/main.py")], "files_read": 5}
        result = node(state)
        assert result["files_read"] == 6

    def test_repeated_invocation_accumulates(self, node, suspect: Callable[..., Suspect]) -> None:
        """Simulated retry: two inspection passes accumulate correctly."""
        state: dict = {"suspects": [suspect("src/main.py")]}
        after_first = node(state)
        assert after_first["files_read"] == 1

        # Second pass (retry): previous count is in state
        after_second = node(after_first)
        assert after_second["files_read"] == 2

    def test_multiple_suspects_accumulate(self, node, suspect: Callable[..., Suspect]) -> None:
        """Multiple readable suspects add to the existing count."""
        state = {
            "suspects": [suspect("src/main.py"), suspect("src/calc.py")],
            "files_read": 3,
        }
        result = node(state)
        assert result["files_read"] == 5  # 3 + 2

    def test_no_suspects_does_not_change_existing_count(self, node) -> None:
        """Empty suspects list returns state unchanged, preserving files_read."""
        state = {"suspects": [], "files_read": 7}
        result = node(state)
        assert result.get("files_read", 0) == 7

    def test_invalid_suspect_path_not_counted(self, node, suspect: Callable[..., Suspect]) -> None:
        """Unreadable/missing suspects do not increment the count."""
        state = {"suspects": [suspect("nonexistent.py")], "files_read": 2}
        result = node(state)
        # No valid snippets → node returns state unchanged
        assert result.get("files_read", 0) == 2

    def test_invalid_line_start_not_counted(self, node, suspect: Callable[..., Suspect]) -> None:
        """Suspects with line_start < 1 are rejected and not counted."""
        state = {"suspects": [suspect("src/main.py", start=0, end=2)], "files_read": 4}
        result = node(state)
        assert result.get("files_read", 0) == 4

    def test_investigation_result_reflects_cumulative(
        self,
        node,
        suspect: Callable[..., Suspect],
    ) -> None:
        """Final InvestigationResult carries the accumulated files_read value."""
        from ex04.shared.types_results import InvestigationResult

        # Verify the state key name matches what AgentService surfaces
        state = {"suspects": [suspect("src/main.py")], "files_read": 10}
        result = node(state)
        assert result["files_read"] == 11

        # Verify InvestigationResult accepts files_read
        inv = InvestigationResult(root_cause="test", files_read=result["files_read"])
        assert inv.files_read == 11
