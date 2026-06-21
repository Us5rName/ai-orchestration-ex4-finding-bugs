"""Code Inspection Node — fetches relevant code snippets.

Fetches code snippets for the top-ranked suspects, records
files read for comparison metrics, and uses the gatekeeper
to perform LLM-assisted inspection analysis of the snippets.

Implementation: **Phase 4** (T4.12)
"""

from __future__ import annotations

import logging
from pathlib import Path

from ex04.services.agent.deps import NodeDeps
from ex04.services.agent.nodes import common
from ex04.services.agent.state import AgentState
from ex04.shared.gatekeeper import GatekeeperInterface
from ex04.shared.types_results import Suspect

logger = logging.getLogger(__name__)

_INSPECTION_PROMPT = (
    "You are a code reviewer. The following code snippets are suspected to contain a bug.\n"
    "Highlight any suspicious patterns, off-by-one errors, null dereferences, "
    "incorrect logic, or resource leaks you observe. Be concise.\n\n"
    "Code snippets:\n{snippets}"
)


class CodeInspectionNode:
    """Fetches code snippets for ranked suspects and performs LLM analysis.

    Reads source files for each suspect location (line_start to line_end),
    formats them as structured text with file path headers and line numbers,
    records the number of files read for comparison metrics, and optionally
    calls the LLM via the gatekeeper to highlight suspicious patterns.

    Attributes:
        target_path: Root directory of the target codebase.
        gatekeeper: Optional gatekeeper for LLM inspection calls.
        provider: LLM provider name forwarded to the gatekeeper.
    """

    def __init__(
        self,
        target_path: Path,
        gatekeeper: GatekeeperInterface | None = None,
        provider: str = "openai",
    ) -> None:
        """Initialize with the target codebase root and optional gatekeeper.

        Args:
            target_path: Root directory of the codebase being investigated.
            gatekeeper: Optional gatekeeper used for LLM inspection calls.
            provider: LLM provider name passed to the gatekeeper.
        """
        self.target_path = target_path
        self.deps = NodeDeps(
            gatekeeper=gatekeeper,
            provider=provider,
            target_path=Path(target_path),
        )

    def __call__(self, state: AgentState) -> AgentState:
        """Inspect code for all ranked suspects.

        Reads source files, formats snippets, accumulates files_read
        (cumulative across retries), calls the gatekeeper LLM.

        Args:
            state: Current agent state with suspects list.

        Returns:
            State with inspected_code, files_read, and token_usage updated.
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

        if not snippets:
            logger.info("CodeInspectionNode: no valid snippets extracted")
            return state

        raw_code = "\n".join(snippets)
        prompt = _INSPECTION_PROMPT.format(snippets=raw_code)
        response = common.call_llm(self.deps, state, "inspect", prompt)
        analysis = response.text.strip()

        inspected = raw_code
        if analysis:
            inspected = f"{raw_code}\n\n## Inspection Analysis\n{analysis}"

        previous_reads = state.get("files_read", 0)
        return {
            **common.state_with_tokens(state, response),
            "inspected_code": inspected,
            "files_read": previous_reads + len(snippets),
        }

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
        body = "\n".join(
            f"{ln}: {line}" for ln, line in enumerate(lines[start - 1 : end], start)
        )
        logger.info(
            "CodeInspectionNode: read %d lines from %s",
            end - start + 1,
            suspect.file_path,
        )
        return f"{header}\n{body}"


def build_inspect_node(deps: NodeDeps) -> CodeInspectionNode:
    """Build the inspection node from workflow dependencies."""
    return CodeInspectionNode(deps.target_path, deps.gatekeeper, deps.provider)
