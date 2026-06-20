"""Note Manager — creates, reads, updates vault markdown notes.

Provides utilities for creating, updating, and managing Obsidian vault
notes with proper frontmatter, wikilinks, and slugified filenames.

## Contract (VaultServiceInterface)

| Method | Input | Output | Phase |
|---|---|---|---|
| `update(note_type, content)` | str, str | Path | P4 |

Implementation: **Phase 4** (T4.06)
"""

from __future__ import annotations

import logging
import re
from datetime import datetime
from pathlib import Path

logger = logging.getLogger(__name__)

# Special note types that go in the vault root
_ROOT_NOTES = {"index", "hot"}


class NoteManager:
    """Manages creation and updates of vault markdown notes.

    Handles frontmatter generation, slugified filenames, wikilinks,
    and routing notes to the correct directory (root vs notes/).

    Attributes:
        vault_path: Path to the root of the vault directory.
    """

    def __init__(self, vault_path: Path) -> None:
        """Initialize with the vault root directory.

        Args:
            vault_path: Root directory of the Obsidian vault.
        """
        self.vault_path = vault_path

    def update(self, note_type: str, content: str) -> Path:
        """Update or create a vault note.

        Routes special note types (index, hot) to the vault root and
        all others to the notes/ subdirectory. Generates frontmatter
        with title, tags, and date.

        Args:
            note_type: Type of note to update (e.g. 'hot', 'index').
            content: New markdown content for the note.

        Returns:
            Path to the updated or created note file.
        """
        if note_type in _ROOT_NOTES:
            path = self.vault_path / f"{note_type}.md"
        else:
            path = self.vault_path / "notes" / f"{note_type}.md"

        path.parent.mkdir(parents=True, exist_ok=True)
        frontmatter = self._build_frontmatter(note_type)
        path.write_text(f"{frontmatter}\n{content}", encoding="utf-8")
        logger.info("Updated note: %s", path)
        return path

    def create_note(self, title: str, content: str, links: list[str]) -> Path:
        """Create a linked markdown note.

        Generates a slugified filename from the title, creates frontmatter,
        and appends wikilinks for related notes.

        Args:
            title: Display title for the note.
            content: Main markdown content of the note.
            links: List of related note titles for wikilinks.

        Returns:
            Path to the created note file.
        """
        slug = self._slugify(title)
        path = self.vault_path / "notes" / f"{slug}.md"
        path.parent.mkdir(parents=True, exist_ok=True)

        frontmatter = self._build_frontmatter(slug, title=title)
        wikilinks = "\n".join(f"- [[{link}]]" for link in links) if links else ""

        note_content = f"{frontmatter}\n# {title}\n\n{content}"
        if wikilinks:
            note_content += f"\n\n## Related\n{wikilinks}"

        path.write_text(note_content, encoding="utf-8")
        logger.info("Created note: %s", path)
        return path

    def update_note(self, path: Path, content: str) -> None:
        """Append content to an existing note or create it if missing.

        Args:
            path: Path to the note file to update.
            content: Content to append to the note.
        """
        path.parent.mkdir(parents=True, exist_ok=True)
        if path.exists():
            existing = path.read_text(encoding="utf-8")
            path.write_text(f"{existing}{content}", encoding="utf-8")
        else:
            path.write_text(content, encoding="utf-8")
        logger.info("Updated note by path: %s", path)

    @staticmethod
    def _build_frontmatter(note_type: str, title: str | None = None) -> str:
        """Build YAML frontmatter for a vault note.

        Args:
            note_type: The note type used as the default title.
            title: Optional explicit title (overrides note_type).

        Returns:
            YAML frontmatter string.
        """
        display_title = title or note_type
        lines = [
            "---",
            f'title: "{display_title}"',
            f"tags: [note, {note_type}]",
            f"date: {datetime.now().strftime('%Y-%m-%d')}",
            "---",
        ]
        return "\n".join(lines)

    @staticmethod
    def _slugify(value: str) -> str:
        """Convert a string to a URL-safe slug for filenames.

        Args:
            value: The string to slugify.

        Returns:
            Lowercase slug with spaces and special chars replaced by hyphens.
        """
        slug = value.lower().strip()
        slug = re.sub(r"[^a-z0-9\s-]", "", slug)
        slug = re.sub(r"[\s]+", "_", slug)
        slug = re.sub(r"-+", "-", slug)
        return slug.strip("-")
