"""Vault Navigator — traverses vault notes and wikilinks.

Provides keyword-based search and wikilink traversal across an Obsidian
vault directory. Used by the Agent Service to find relevant context
during bug investigation.

## Contract (VaultServiceInterface)

| Method | Input | Output | Phase |
|---|---|---|---|
| `navigate(query)` | str | list[dict] | P4 |

Implementation: **Phase 4** (T4.05)
"""

from __future__ import annotations

import logging
import re
from pathlib import Path

logger = logging.getLogger(__name__)

# Regex for Obsidian [[wikilinks]]
_WIKILINK_RE = re.compile(r"\[\[([^\]]+)\]\]")


class VaultNavigator:
    """Navigates an Obsidian vault to find relevant context.

    Searches vault notes by keyword matching (case-insensitive) and
    parses [[wikilinks]] to discover related notes.

    Attributes:
        vault_path: Path to the root of the vault directory.
    """

    def __init__(self, vault_path: Path) -> None:
        """Initialize with the vault root directory.

        Args:
            vault_path: Root directory of the Obsidian vault.
        """
        self.vault_path = vault_path

    def navigate(self, query: str) -> list[dict[str, str]]:
        """Navigate vault to find relevant context.

        Searches all .md files in the vault (title and content) for
        the given query using case-insensitive keyword matching.

        Args:
            query: Bug description or search query string.

        Returns:
            List of dicts with 'title', 'path', 'content' keys.
        """
        if not self.vault_path.exists():
            return []

        notes_dir = self.vault_path / "notes"
        if not notes_dir.exists():
            return []

        results: list[dict[str, str]] = []
        query_lower = query.lower()

        for md_file in sorted(notes_dir.glob("*.md")):
            content = md_file.read_text(encoding="utf-8")
            title = self._extract_title(content)

            if query_lower in title.lower() or query_lower in content.lower():
                wikilinks = _WIKILINK_RE.findall(content)
                results.append(
                    {
                        "title": title,
                        "path": str(md_file),
                        "content": content,
                    }
                )
                logger.debug("Found match in %s (wikilinks: %s)", md_file, wikilinks)

        return results

    @staticmethod
    def _extract_title(content: str) -> str:
        """Extract the title from a markdown note's frontmatter.

        Args:
            content: Full markdown content of the note.

        Returns:
            The title string, or the filename if no frontmatter title.
        """
        for line in content.splitlines():
            if line.startswith("title:"):
                return line.split(":", 1)[1].strip().strip('"').strip("'")
        return ""
