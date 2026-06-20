"""Vault Navigator — traverses vault notes and wikilinks.

Provides keyword-based search and wikilink traversal across an Obsidian
vault directory. Used by the Agent Service to find relevant context
during bug investigation.

## Contract (VaultServiceInterface)

| Method | Input | Output | Phase |
|---|---|---|---|
| `find_relevant_notes(query)` | str | list[dict] | P4 |
| `navigate_from_index(target)` | str | list[dict] | P4 |

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
        """Backward-compatible alias for ``find_relevant_notes``."""
        return self.find_relevant_notes(query)

    def find_relevant_notes(self, query: str) -> list[dict[str, str]]:
        """Find relevant notes by keyword.

        Searches all .md files in the vault (title and content) for
        the given query using case-insensitive keyword matching.

        Args:
            query: Bug description or search query string.

        Returns:
            List of dicts with 'title', 'path', 'content' keys.
        """
        # An empty/whitespace query would substring-match every note; treat
        # it as "no query" and return nothing rather than the whole vault.
        if not query.strip():
            return []

        if not self.vault_path.exists():
            return []

        results: list[dict[str, str]] = []
        query_lower = query.lower()

        # Search every note in the vault, including the curated root-level
        # index.md and hot.md (the bug focus area), not just notes/.
        for md_file in sorted(self.vault_path.rglob("*.md")):
            content = md_file.read_text(encoding="utf-8")
            title = self._extract_title(content, md_file)

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

    def navigate_from_index(self, target: str) -> list[dict[str, str]]:
        """Follow index wikilinks and return notes relevant to ``target``.

        Args:
            target: Case-insensitive note title, path stem, or content keyword.

        Returns:
            Linked notes from index.md that match the target. Missing and broken
            links are ignored.
        """
        if not target.strip():
            return []
        index = self.vault_path / "index.md"
        if not index.is_file():
            return []

        matches: list[dict[str, str]] = []
        target_lower = target.lower()
        for link in _WIKILINK_RE.findall(index.read_text(encoding="utf-8")):
            note = self._resolve_note(link)
            if note is None:
                continue
            content = note.read_text(encoding="utf-8")
            title = self._extract_title(content, note)
            haystack = f"{title}\n{note.stem}\n{content}".lower()
            if target_lower in haystack:
                matches.append({"title": title, "path": str(note), "content": content})
        return matches

    def _resolve_note(self, link: str) -> Path | None:
        """Resolve an Obsidian wikilink to a markdown file in the vault."""
        clean = link.split("|", 1)[0].split("#", 1)[0].strip()
        candidates = [self.vault_path / f"{clean}.md", self.vault_path / "notes" / f"{clean}.md"]
        for candidate in candidates:
            if candidate.is_file():
                return candidate
        return None

    @staticmethod
    def _extract_title(content: str, md_file: Path) -> str:
        """Extract the title from a markdown note's frontmatter.

        Args:
            content: Full markdown content of the note.
            md_file: Path to the note, used for the filename fallback.

        Returns:
            The frontmatter title, or the filename stem if none is present.
        """
        for line in content.splitlines():
            if line.startswith("title:"):
                return line.split(":", 1)[1].strip().strip('"').strip("'")
        return md_file.stem
