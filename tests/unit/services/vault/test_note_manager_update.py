"""Tests for NoteManager.update() (T4.06 interface contract).

Tests vault note creation, overwriting, frontmatter, and routing.
"""

from __future__ import annotations

import tempfile
from pathlib import Path

from ex04.services.vault.note_manager import NoteManager


class TestNoteManagerUpdate:
    """Tests for NoteManager.update() method (interface contract)."""

    def test_update_creates_note_file(self) -> None:
        """Test that update() creates a note file when it doesn't exist."""
        with tempfile.TemporaryDirectory() as tmpdir:
            vault_path = Path(tmpdir) / "test_vault"
            vault_path.mkdir(parents=True, exist_ok=True)
            manager = NoteManager(vault_path=vault_path)
            result = manager.update("hot", "# Hot Area\n\nBug content")

            assert result.exists()
            assert result.name == "hot.md"

    def test_update_overwrites_existing_note(self) -> None:
        """Test that update() overwrites existing note content."""
        with tempfile.TemporaryDirectory() as tmpdir:
            vault_path = Path(tmpdir) / "test_vault"
            vault_path.mkdir(parents=True, exist_ok=True)
            manager = NoteManager(vault_path=vault_path)

            manager.update("hot", "old content")
            manager.update("hot", "new content")

            content = (vault_path / "hot.md").read_text(encoding="utf-8")
            assert "new content" in content
            assert "old content" not in content

    def test_update_returns_path(self) -> None:
        """Test that update() returns a valid Path."""
        with tempfile.TemporaryDirectory() as tmpdir:
            vault_path = Path(tmpdir) / "test_vault"
            vault_path.mkdir(parents=True, exist_ok=True)
            manager = NoteManager(vault_path=vault_path)
            result = manager.update("index", "# Index")

            assert isinstance(result, Path)
            assert result.exists()

    def test_update_generates_frontmatter(self) -> None:
        """Test that update() generates frontmatter with title, tags, date."""
        with tempfile.TemporaryDirectory() as tmpdir:
            vault_path = Path(tmpdir) / "test_vault"
            vault_path.mkdir(parents=True, exist_ok=True)
            manager = NoteManager(vault_path=vault_path)
            manager.update("hot", "content")

            content = (vault_path / "hot.md").read_text(encoding="utf-8")
            assert content.startswith("---")
            assert "tags:" in content
            assert "date:" in content

    def test_update_creates_in_notes_subdir(self) -> None:
        """Test that update() creates notes in the notes/ subdirectory."""
        with tempfile.TemporaryDirectory() as tmpdir:
            vault_path = Path(tmpdir) / "test_vault"
            vault_path.mkdir(parents=True, exist_ok=True)
            manager = NoteManager(vault_path=vault_path)
            manager.update("auth_module", "auth content")

            assert (vault_path / "notes" / "auth_module.md").exists()

    def test_update_special_note_types_in_root(self) -> None:
        """Test that special note types (index, hot) go in vault root."""
        with tempfile.TemporaryDirectory() as tmpdir:
            vault_path = Path(tmpdir) / "test_vault"
            vault_path.mkdir(parents=True, exist_ok=True)
            manager = NoteManager(vault_path=vault_path)
            result = manager.update("index", "# Index content")

            assert result == vault_path / "index.md"
            assert result.exists()
