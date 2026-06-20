"""Core tests for VaultBuilder (T4.04).

Tests directory creation, vault structure, and return values.
"""

from __future__ import annotations

import tempfile
from pathlib import Path

from ex04.services.vault.builder import VaultBuilder
from ex04.shared.types import Entity, GraphData


class TestVaultBuilderCore:
    """Tests for VaultBuilder directory structure and return values."""

    def test_build_creates_vault_directory(self) -> None:
        """Test that build() creates the vault directory."""
        graph_data = GraphData()

        with tempfile.TemporaryDirectory() as tmpdir:
            vault_path = Path(tmpdir) / "test_vault"
            builder = VaultBuilder(vault_path=vault_path)
            builder.build(graph_data)

            assert vault_path.exists()
            assert vault_path.is_dir()

    def test_build_returns_dict_with_paths(self) -> None:
        """Test that build() returns dict mapping note types to paths."""
        graph_data = GraphData()

        with tempfile.TemporaryDirectory() as tmpdir:
            vault_path = Path(tmpdir) / "test_vault"
            builder = VaultBuilder(vault_path=vault_path)
            result = builder.build(graph_data)

            assert isinstance(result, dict)
            assert "index" in result
            assert result["index"] == vault_path / "index.md"

    def test_build_handles_empty_graph(self) -> None:
        """Test that build() handles empty graph data gracefully."""
        graph_data = GraphData(entities=[], relationships=[], communities=[])

        with tempfile.TemporaryDirectory() as tmpdir:
            vault_path = Path(tmpdir) / "test_vault"
            builder = VaultBuilder(vault_path=vault_path)
            builder.build(graph_data)

            assert vault_path.exists()
            assert (vault_path / "index.md").exists()

    def test_build_creates_notes_subdirectory(self) -> None:
        """Test that build() creates a notes/ subdirectory for entity notes."""
        entities = [Entity(name="TestEntity", kind="class")]
        graph_data = GraphData(entities=entities)

        with tempfile.TemporaryDirectory() as tmpdir:
            vault_path = Path(tmpdir) / "test_vault"
            builder = VaultBuilder(vault_path=vault_path)
            builder.build(graph_data)

            notes_dir = vault_path / "notes"
            assert notes_dir.exists()
            assert notes_dir.is_dir()

    def test_build_sanitizes_path_like_entity_names(self) -> None:
        """Path-like / traversal entity names must not crash or escape notes/."""
        entities = [
            Entity(name="pkg/sub/mod", kind="file"),
            Entity(name="../escape", kind="class"),
        ]
        graph_data = GraphData(entities=entities)

        with tempfile.TemporaryDirectory() as tmpdir:
            vault_path = Path(tmpdir) / "test_vault"
            builder = VaultBuilder(vault_path=vault_path)
            builder.build(graph_data)  # must not raise FileNotFoundError

            notes_dir = vault_path / "notes"
            written = list(notes_dir.glob("*.md"))
            assert len(written) == 2
            # Every note stays directly inside notes/ (no traversal, no subdirs).
            assert all(p.parent == notes_dir for p in written)
            assert not (vault_path.parent / "escape.md").exists()
