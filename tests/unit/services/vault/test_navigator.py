"""Tests for VaultNavigator implementation (T4.05).

Tests VaultNavigator.navigate() against VaultServiceInterface contract:
- Searches vault notes by keyword matching
- Parses [[wikilinks]] from Markdown
- Handles missing notes and broken links
- Returns list of dicts with 'title', 'path', 'content' keys
"""

from __future__ import annotations

import tempfile
from pathlib import Path

from ex04.services.vault.navigator import VaultNavigator


class TestVaultNavigator:
    """Tests for VaultNavigator.navigate() method."""

    def _setup_vault(self, vault_path: Path) -> None:
        """Create a minimal vault with sample notes."""
        vault_path.mkdir(parents=True, exist_ok=True)
        notes_dir = vault_path / "notes"
        notes_dir.mkdir(parents=True, exist_ok=True)

        (notes_dir / "auth.md").write_text(
            "---\ntitle: auth\n---\n# Auth\n\nHandles authentication.",
            encoding="utf-8",
        )
        (notes_dir / "user.md").write_text(
            "---\ntitle: User\n---\n# User\n\n[[auth]] manages users.",
            encoding="utf-8",
        )

    def test_navigate_returns_list_of_dicts(self) -> None:
        """Test that navigate() returns a list of dicts."""
        with tempfile.TemporaryDirectory() as tmpdir:
            vault_path = Path(tmpdir) / "test_vault"
            self._setup_vault(vault_path)
            navigator = VaultNavigator(vault_path=vault_path)
            results = navigator.navigate("authentication")

            assert isinstance(results, list)
            if results:
                assert "title" in results[0]
                assert "path" in results[0]
                assert "content" in results[0]

    def test_navigate_finds_matching_notes(self) -> None:
        """Test that navigate() finds notes matching the query."""
        with tempfile.TemporaryDirectory() as tmpdir:
            vault_path = Path(tmpdir) / "test_vault"
            self._setup_vault(vault_path)
            navigator = VaultNavigator(vault_path=vault_path)
            results = navigator.navigate("authentication")

            assert len(results) >= 1
            titles = [r["title"] for r in results]
            assert "auth" in titles

    def test_navigate_case_insensitive(self) -> None:
        """Test that navigate() search is case-insensitive."""
        with tempfile.TemporaryDirectory() as tmpdir:
            vault_path = Path(tmpdir) / "test_vault"
            self._setup_vault(vault_path)
            navigator = VaultNavigator(vault_path=vault_path)
            results = navigator.navigate("AUTH")

            assert len(results) >= 1

    def test_navigate_empty_result_for_no_match(self) -> None:
        """Test that navigate() returns empty list when no notes match."""
        with tempfile.TemporaryDirectory() as tmpdir:
            vault_path = Path(tmpdir) / "test_vault"
            self._setup_vault(vault_path)
            navigator = VaultNavigator(vault_path=vault_path)
            results = navigator.navigate("nonexistent_keyword_xyz")

            assert results == []

    def test_navigate_searches_title_and_content(self) -> None:
        """Test that navigate() searches both title and content."""
        with tempfile.TemporaryDirectory() as tmpdir:
            vault_path = Path(tmpdir) / "test_vault"
            self._setup_vault(vault_path)
            navigator = VaultNavigator(vault_path=vault_path)
            results = navigator.navigate("User")

            assert len(results) >= 1
            titles = [r["title"] for r in results]
            assert "User" in titles

    def test_navigate_empty_vault(self) -> None:
        """Test that navigate() handles empty vault gracefully."""
        with tempfile.TemporaryDirectory() as tmpdir:
            vault_path = Path(tmpdir) / "test_vault"
            vault_path.mkdir(parents=True, exist_ok=True)
            navigator = VaultNavigator(vault_path=vault_path)
            results = navigator.navigate("any query")

            assert results == []

    def test_navigate_handles_missing_notes_dir(self) -> None:
        """Test that navigate() handles vault without notes directory."""
        with tempfile.TemporaryDirectory() as tmpdir:
            vault_path = Path(tmpdir) / "test_vault"
            vault_path.mkdir(parents=True, exist_ok=True)
            navigator = VaultNavigator(vault_path=vault_path)
            results = navigator.navigate("any query")

            assert results == []

    def test_navigate_parses_wikilinks(self) -> None:
        """Test that navigate() correctly parses [[wikilinks]] in content."""
        with tempfile.TemporaryDirectory() as tmpdir:
            vault_path = Path(tmpdir) / "test_vault"
            self._setup_vault(vault_path)
            navigator = VaultNavigator(vault_path=vault_path)
            results = navigator.navigate("auth")

            # Should find user.md which contains [[auth]]
            paths = [Path(r["path"]).name for r in results]
            assert "user.md" in paths

    def test_navigate_returns_content_field(self) -> None:
        """Test that navigate() returns non-empty content in results."""
        with tempfile.TemporaryDirectory() as tmpdir:
            vault_path = Path(tmpdir) / "test_vault"
            self._setup_vault(vault_path)
            navigator = VaultNavigator(vault_path=vault_path)
            results = navigator.navigate("authentication")

            assert len(results) >= 1
            assert len(results[0]["content"]) > 0

    def test_navigate_returns_path_field(self) -> None:
        """Test that navigate() returns valid path in results."""
        with tempfile.TemporaryDirectory() as tmpdir:
            vault_path = Path(tmpdir) / "test_vault"
            self._setup_vault(vault_path)
            navigator = VaultNavigator(vault_path=vault_path)
            results = navigator.navigate("authentication")

            assert len(results) >= 1
            assert Path(results[0]["path"]).exists()
