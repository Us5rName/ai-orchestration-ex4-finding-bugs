"""Content structure tests for VaultBuilder (T4.04).

Tests index.md, entity notes, hot.md, wikilinks, and community rendering.
"""

from __future__ import annotations

import tempfile
from pathlib import Path

from ex04.services.vault.builder import VaultBuilder
from ex04.shared.types import Community, Entity, GraphData, Relationship


class TestVaultBuilderContent:
    """Tests for VaultBuilder markdown content structure."""

    def test_build_creates_index_md(self) -> None:
        """Test that build() creates index.md with navigation structure."""
        entities = [
            Entity(name="auth.py", kind="file"),
            Entity(name="User", kind="class", file_path="auth.py"),
        ]
        graph_data = GraphData(entities=entities)

        with tempfile.TemporaryDirectory() as tmpdir:
            vault_path = Path(tmpdir) / "test_vault"
            builder = VaultBuilder(vault_path=vault_path)
            builder.build(graph_data)

            index_path = vault_path / "index.md"
            assert index_path.exists()
            content = index_path.read_text(encoding="utf-8")
            assert "# Graph Index" in content

    def test_build_creates_entity_notes(self) -> None:
        """Test that build() creates individual entity notes."""
        entities = [
            Entity(name="User", kind="class", file_path="auth.py", line_range=(1, 50)),
        ]
        graph_data = GraphData(entities=entities)

        with tempfile.TemporaryDirectory() as tmpdir:
            vault_path = Path(tmpdir) / "test_vault"
            builder = VaultBuilder(vault_path=vault_path)
            builder.build(graph_data)

            entity_note = vault_path / "notes" / "User.md"
            assert entity_note.exists()
            content = entity_note.read_text(encoding="utf-8")
            assert "## Properties" in content
            assert "- **Kind**: class" in content

    def test_build_creates_hot_md(self) -> None:
        """Test that build() creates hot.md for bug focus area."""
        entities = [Entity(name="auth.py", kind="file")]
        graph_data = GraphData(entities=entities)

        with tempfile.TemporaryDirectory() as tmpdir:
            vault_path = Path(tmpdir) / "test_vault"
            builder = VaultBuilder(vault_path=vault_path)
            builder.build(graph_data)

            hot_path = vault_path / "hot.md"
            assert hot_path.exists()
            content = hot_path.read_text(encoding="utf-8")
            assert "# Hot Area" in content

    def test_build_uses_wikilinks_syntax(self) -> None:
        """Test that build() uses [[wikilinks]] syntax for Obsidian."""
        entities = [
            Entity(name="User", kind="class", file_path="auth.py"),
            Entity(name="Auth", kind="class", file_path="auth.py"),
        ]
        relationships = [Relationship(source="User", target="Auth", type="calls")]
        graph_data = GraphData(entities=entities, relationships=relationships)

        with tempfile.TemporaryDirectory() as tmpdir:
            vault_path = Path(tmpdir) / "test_vault"
            builder = VaultBuilder(vault_path=vault_path)
            builder.build(graph_data)

            user_note = vault_path / "notes" / "User.md"
            content = user_note.read_text(encoding="utf-8")
            assert "[[Auth]]" in content

    def test_build_creates_communities_section(self) -> None:
        """Test that build() includes communities in index.md."""
        communities = [
            Community(name="Auth Module", entities=["User", "Auth"], size=2),
        ]
        graph_data = GraphData(communities=communities)

        with tempfile.TemporaryDirectory() as tmpdir:
            vault_path = Path(tmpdir) / "test_vault"
            builder = VaultBuilder(vault_path=vault_path)
            builder.build(graph_data)

            index_path = vault_path / "index.md"
            content = index_path.read_text(encoding="utf-8")
            assert "Auth Module" in content

    def test_build_includes_relationships_in_index(self) -> None:
        """Test that build() includes relationships in index.md."""
        relationships = [Relationship(source="User", target="Auth", type="calls")]
        graph_data = GraphData(relationships=relationships)

        with tempfile.TemporaryDirectory() as tmpdir:
            vault_path = Path(tmpdir) / "test_vault"
            builder = VaultBuilder(vault_path=vault_path)
            builder.build(graph_data)

            index_path = vault_path / "index.md"
            content = index_path.read_text(encoding="utf-8")
            assert "User" in content
            assert "Auth" in content
