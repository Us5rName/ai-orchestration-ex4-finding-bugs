"""Vault service facade implementing the vault contract."""

from __future__ import annotations

from pathlib import Path

from ex04.services.vault.builder import VaultBuilder
from ex04.services.vault.interface import VaultServiceInterface
from ex04.services.vault.navigator import VaultNavigator
from ex04.services.vault.note_manager import NoteManager
from ex04.shared.types import GraphData


class VaultService(VaultServiceInterface):
    """Coordinate vault building, navigation, and note updates."""

    def __init__(self, vault_path: Path) -> None:
        """Initialize service components for a vault root."""
        self.vault_path = vault_path
        self._builder = VaultBuilder(vault_path)
        self._navigator = VaultNavigator(vault_path)
        self._notes = NoteManager(vault_path)

    def build(self, graph_data: GraphData) -> dict[str, Path]:
        """Build an Obsidian vault from graph data."""
        return self._builder.build(graph_data)

    def navigate(self, query: str) -> list[dict[str, str]]:
        """Find relevant vault notes for a query."""
        return self._navigator.navigate(query)

    def update(self, note_type: str, content: str) -> Path:
        """Update or create a note in the vault."""
        return self._notes.update(note_type, content)
