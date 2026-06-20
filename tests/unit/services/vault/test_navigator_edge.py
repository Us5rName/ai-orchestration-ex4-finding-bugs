"""Edge-case tests for VaultNavigator."""

from __future__ import annotations

import tempfile
from pathlib import Path

from ex04.services.vault.navigator import VaultNavigator


def _setup_vault(vault_path: Path) -> None:
    """Create a minimal vault with linked sample notes."""
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


def test_navigate_title_falls_back_to_filename() -> None:
    """A note without a frontmatter title uses its filename stem as title."""
    with tempfile.TemporaryDirectory() as tmpdir:
        vault_path = Path(tmpdir) / "test_vault"
        notes_dir = vault_path / "notes"
        notes_dir.mkdir(parents=True, exist_ok=True)
        (notes_dir / "no_title.md").write_text(
            "# Heading\n\npayment logic here", encoding="utf-8"
        )
        results = VaultNavigator(vault_path=vault_path).navigate("payment")

        assert "no_title" in [result["title"] for result in results]


def test_navigate_empty_vault() -> None:
    """Test that navigate() handles empty vault gracefully."""
    with tempfile.TemporaryDirectory() as tmpdir:
        vault_path = Path(tmpdir) / "test_vault"
        vault_path.mkdir(parents=True, exist_ok=True)
        assert VaultNavigator(vault_path=vault_path).navigate("any query") == []


def test_navigate_handles_missing_notes_dir() -> None:
    """Test that navigate() handles vault without notes directory."""
    with tempfile.TemporaryDirectory() as tmpdir:
        vault_path = Path(tmpdir) / "test_vault"
        vault_path.mkdir(parents=True, exist_ok=True)
        assert VaultNavigator(vault_path=vault_path).navigate("any query") == []


def test_navigate_parses_wikilinks() -> None:
    """Test that navigate() correctly parses [[wikilinks]] in content."""
    with tempfile.TemporaryDirectory() as tmpdir:
        vault_path = Path(tmpdir) / "test_vault"
        _setup_vault(vault_path)
        results = VaultNavigator(vault_path=vault_path).navigate("auth")

        assert "user.md" in [Path(result["path"]).name for result in results]


def test_navigate_returns_content_field() -> None:
    """Test that navigate() returns non-empty content in results."""
    with tempfile.TemporaryDirectory() as tmpdir:
        vault_path = Path(tmpdir) / "test_vault"
        _setup_vault(vault_path)
        results = VaultNavigator(vault_path=vault_path).navigate("authentication")

        assert len(results[0]["content"]) > 0


def test_navigate_returns_path_field() -> None:
    """Test that navigate() returns valid path in results."""
    with tempfile.TemporaryDirectory() as tmpdir:
        vault_path = Path(tmpdir) / "test_vault"
        _setup_vault(vault_path)
        results = VaultNavigator(vault_path=vault_path).navigate("authentication")

        assert Path(results[0]["path"]).exists()
