"""Diagram Generator — generates and validates Mermaid diagrams.

Saves Mermaid diagram content to markdown files and validates basic
Mermaid syntax (fenced code blocks with mermaid keyword).

## Contract (AnalysisServiceInterface)

| Method | Input | Output | Phase |
|---|---|---|---|
| `save_diagram(content, name, path)` | str, str, Path | Path | P4 |
| `validate_mermaid(content)` | str | bool | P4 |

Implementation: **Phase 4** (T4.17)
"""

from __future__ import annotations

import logging
from pathlib import Path

logger = logging.getLogger(__name__)


class DiagramGenerator:
    """Generates and validates Mermaid diagrams.

    Saves diagram content to .md files and validates that content
    contains properly fenced Mermaid code blocks.

    Attributes:
        None — stateless utility class.
    """

    @staticmethod
    def validate_mermaid(content: str | None) -> bool:
        """Validate that content contains a properly fenced Mermaid block.

        Checks for:
        - Non-empty, non-None content
        - Opening ```mermaid fence
        - Closing ``` fence

        Args:
            content: Mermaid diagram content to validate.

        Returns:
            True if content has valid fenced mermaid block, False otherwise.
        """
        if not content:
            return False

        has_opening = "```mermaid" in content
        has_closing = content.count("```") >= 2

        return has_opening and has_closing

    def save_diagram(self, content: str, name: str, path: Path) -> Path:
        """Save a Mermaid diagram to a .md file.

        Creates parent directories if they don't exist, then writes
        the content to {path}/{name}.md.

        Args:
            content: Mermaid diagram content to save.
            name: Diagram name (used as filename without extension).
            path: Directory path to save the file into.

        Returns:
            Path to the created .md file.
        """
        output_path = path / f"{name}.md"
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_text(content, encoding="utf-8")
        logger.info("Saved diagram: %s", output_path)
        return output_path
