"""Fix Generation Node — proposes and applies code fix.

Generates a fix based on the root cause analysis and applies
it to the target file.

Implementation: **Phase 4** (T4.14)
"""

from __future__ import annotations

import difflib
import logging
from pathlib import Path

from ex04.services.agent.deps import NodeDeps
from ex04.services.agent.nodes import common
from ex04.services.agent.state import AgentState
from ex04.shared.gatekeeper import GatekeeperInterface

logger = logging.getLogger(__name__)


class FixGenerationNode:
    """Generates and applies a code fix.

    Uses the gatekeeper to call the LLM with the root cause
    and produces a proposed fix, then applies it.

    Attributes:
        None — stateless node.
    """

    def __init__(
        self,
        target_path: Path | str = ".",
        gatekeeper: GatekeeperInterface | None = None,
        provider: str = "openai",
    ) -> None:
        """Initialize with target root and optional Gatekeeper dependency."""
        self.target_path = Path(target_path)
        self.deps = NodeDeps(
            gatekeeper=gatekeeper,
            provider=provider,
            target_path=self.target_path,
        )

    def __call__(self, state: AgentState) -> AgentState:
        """Generate and apply fix.

        Args:
            state: Current agent state.

        Returns:
            State with proposed_fix and fix_applied populated.
        """
        logger.info("FixGenerationNode: generating fix")
        prompt = (
            "Propose a fix. Optional apply format: FILE:, FIND:, REPLACE:.\n"
            f"Root cause:\n{state.get('root_cause', '')}\n\nCode:\n{state.get('inspected_code', '')}"
        )
        response = common.call_llm(self.deps, state, "fix", prompt)
        proposed = response.text.strip()
        applied, diff = self._apply_replacement(proposed)
        return {
            **common.state_with_tokens(state, response),
            "proposed_fix": proposed,
            "fix_diff": diff,
            "fix_applied": applied,
        }

    def _apply_replacement(self, proposed: str) -> tuple[bool, str]:
        """Apply a simple FILE/FIND/REPLACE model response if present."""
        sections = self._sections(proposed)
        if not {"FILE", "FIND", "REPLACE"} <= sections.keys():
            return False, ""
        file_path = self.target_path / sections["FILE"].strip()
        if not file_path.is_file():
            return False, ""
        original = file_path.read_text(encoding="utf-8")
        if sections["FIND"] not in original:
            return False, ""
        updated = original.replace(sections["FIND"], sections["REPLACE"], 1)
        file_path.write_text(updated, encoding="utf-8")
        return True, self._diff(str(file_path), original, updated)

    @staticmethod
    def _diff(file_path: str, before: str, after: str) -> str:
        """Build a unified diff for an applied fix."""
        return "".join(
            difflib.unified_diff(
                before.splitlines(keepends=True),
                after.splitlines(keepends=True),
                fromfile=f"{file_path}:before",
                tofile=f"{file_path}:after",
            )
        )

    @staticmethod
    def _sections(text: str) -> dict[str, str]:
        """Parse FILE/FIND/REPLACE sections from text."""
        result: dict[str, str] = {}
        current = ""
        for line in text.splitlines():
            if line in {"FILE:", "FIND:", "REPLACE:"}:
                current = line[:-1]
                result[current] = ""
            elif current:
                result[current] = f"{result[current]}{line}\n"
        return {key: value.rstrip("\n") for key, value in result.items()}


def build_fix_node(deps: NodeDeps) -> FixGenerationNode:
    """Build the fix-generation node from workflow dependencies."""
    return FixGenerationNode(deps.target_path, deps.gatekeeper, deps.provider)
