"""Code Inspection Node — fetches relevant code snippets.

Fetches code snippets for the top-ranked suspects and records
files read for comparison metrics.

Implementation: **Phase 4** (T4.12)
"""

from __future__ import annotations

import logging
from pathlib import Path

from ex04.services.agent.state import AgentState
from ex04.shared.types_results import Suspect

logger = logging.getLogger(__name__)


class CodeInspectionNode:
    """Fetches code snippets for ranked suspects.

    Reads source files for each suspect location (line_start to line_end)
    and formats them as structured text with file path headers and line
    numbers. Missing files and invalid ranges are skipped gracefully.

    Attributes:
        target_path: Root directory of the target codebase for resolving
            relative file paths from suspect locations.
    """

    def __init__(self, target_path: Path) -> None:
        """Initialize with the target codebase root.

        Args:
            target_path: Root directory of the codebase being investigated.
        """
        self.target_path = target_path

    def __call__(self, state: AgentState) -> AgentState:
        """Inspect code for all ranked suspects.

        Reads source files for each suspect, formats snippets with file
        path headers and line numbers, and appends to inspected_code.

        Args:
            state: Current agent state with suspects list.

        Returns:
            State with inspected_code populated.
        """
        suspects = state.get("suspects", [])
        if not suspects:
            logger.info("CodeInspectionNode: no suspects to inspect")
            return state

        snippets: list[str] = []
        for suspect in suspects:
            snippet = self._read_snippet(suspect)
            if snippet:
                snippets.append(snippet)

        if snippets:
            return {**state, "inspected_code": "\n".join(snippets)}
        logger.info("CodeInspectionNode: no valid snippets extracted")
        return state

    def _read_snippet(self, suspect: Suspect) -> str | None:
        """Read a code snippet for a single suspect.

        Args:
            suspect: Suspect location with file path and line range.

        Returns:
            Formatted snippet string, or None if the file cannot be read.
        """
        file_path = self.target_path / suspect.file_path
        if not file_path.is_file():
            logger.warning("CodeInspectionNode: file not found: %s", suspect.file_path)
            return None

        if suspect.line_start < 1:
            logger.warning(
                "CodeInspectionNode: invalid line_start=%d in %s (1-based)",
                suspect.line_start,
                suspect.file_path,
            )
            return None

        lines = file_path.read_text(encoding="utf-8").splitlines()
        start = suspect.line_start
        end = min(suspect.line_end, len(lines))

        if start > end:
            logger.warning(
                "CodeInspectionNode: invalid range %d-%d in %s",
                suspect.line_start,
                suspect.line_end,
                suspect.file_path,
            )
            return None

        header = f"--- {suspect.file_path} (lines {start}-{end}) ---"
        body = "\n".join(f"{ln}: {line}" for ln, line in enumerate(lines[start - 1 : end], start))
        logger.info(
            "CodeInspectionNode: read %d lines from %s",
            end - start + 1,
            suspect.file_path,
        )
        return f"{header}\n{body}"
