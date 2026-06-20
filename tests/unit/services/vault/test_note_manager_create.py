"""Tests for NoteManager.create_note() and update_note() (T4.06).

Tests note creation with frontmatter, wikilinks, slugified filenames,
and content appending.
"""

from __future__ import annotations

import tempfile
from pathlib import Path

from ex04.services.vault.note_manager import NoteManager


class TestNoteManagerCreateNote:
    """Tests for NoteManager.create_note() method."""

    def test_create_note_creates_file(self) -> None:
        """Test that create_note() creates a markdown note file."""
        with tempfile.TemporaryDirectory() as tmpdir:
            vault_path = Path(tmpdir) / "test_vault"
            vault_path.mkdir(parents=True, exist_ok=True)
            manager = NoteManager(vault_path=vault_path)
            result = manager.create_note(title="My Note", content="Note body", links=["related"])

            assert result.exists()
            assert result.name == "my_note.md"

    def test_create_note_has_frontmatter(self) -> None:
        """Test that create_note() includes frontmatter."""
        with tempfile.TemporaryDirectory() as tmpdir:
            vault_path = Path(tmpdir) / "test_vault"
            vault_path.mkdir(parents=True, exist_ok=True)
            manager = NoteManager(vault_path=vault_path)
            result = manager.create_note(title="My Note", content="Note body", links=[])

            content = result.read_text(encoding="utf-8")
            assert content.startswith("---")
            assert 'title: "My Note"' in content

    def test_create_note_includes_wikilinks(self) -> None:
        """Test that create_note() includes [[wikilinks]] for related notes."""
        with tempfile.TemporaryDirectory() as tmpdir:
            vault_path = Path(tmpdir) / "test_vault"
            vault_path.mkdir(parents=True, exist_ok=True)
            manager = NoteManager(vault_path=vault_path)
            result = manager.create_note(
                title="My Note", content="Note body", links=["Auth", "User"]
            )

            content = result.read_text(encoding="utf-8")
            assert "[[Auth]]" in content
            assert "[[User]]" in content

    def test_create_note_slugifies_title(self) -> None:
        """Test that create_note() slugifies the title for the filename."""
        with tempfile.TemporaryDirectory() as tmpdir:
            vault_path = Path(tmpdir) / "test_vault"
            vault_path.mkdir(parents=True, exist_ok=True)
            manager = NoteManager(vault_path=vault_path)
            result = manager.create_note(title="My Cool Note!", content="body", links=[])

            assert result.name == "my_cool_note.md"


class TestNoteManagerUpdateNote:
    """Tests for NoteManager.update_note() method."""

    def test_update_note_appends_content(self) -> None:
        """Test that update_note() appends content to existing note."""
        with tempfile.TemporaryDirectory() as tmpdir:
            vault_path = Path(tmpdir) / "test_vault"
            vault_path.mkdir(parents=True, exist_ok=True)
            manager = NoteManager(vault_path=vault_path)

            note_path = vault_path / "notes" / "existing.md"
            note_path.parent.mkdir(parents=True, exist_ok=True)
            note_path.write_text("original content", encoding="utf-8")
            manager.update_note(note_path, "\n## Updated\n\nNew section")

            content = note_path.read_text(encoding="utf-8")
            assert "original content" in content
            assert "New section" in content

    def test_update_note_creates_if_missing(self) -> None:
        """Test that update_note() creates the note if it doesn't exist."""
        with tempfile.TemporaryDirectory() as tmpdir:
            vault_path = Path(tmpdir) / "test_vault"
            vault_path.mkdir(parents=True, exist_ok=True)
            manager = NoteManager(vault_path=vault_path)

            note_path = vault_path / "notes" / "new_note.md"
            manager.update_note(note_path, "brand new content")

            assert note_path.exists()
            assert note_path.read_text(encoding="utf-8") == "brand new content"
