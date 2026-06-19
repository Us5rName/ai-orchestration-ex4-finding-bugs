"""Mock Vault Service — synthetic vault operations for testing."""

from __future__ import annotations

from pathlib import Path

from ex04.services.vault.interface import VaultServiceInterface
from ex04.shared.types import GraphData


class MockVaultService(VaultServiceInterface):
    """Mock implementation of VaultServiceInterface with synthetic data.

    Returns deterministic synthetic vault paths and content for testing
    without creating real Obsidian notes.
    """

    def build(self, graph_data: GraphData) -> dict[str, Path]:
        """Return fake vault note paths.

        Args:
            graph_data: Graph data (ignored in mock).

        Returns:
            Dict mapping note types to fake paths.
        """
        return {
            "index": Path("/tmp/obsidian/index.md"),
            "hot": Path("/tmp/obsidian/hot.md"),
            "entities": Path("/tmp/obsidian/entities.md"),
        }

    def navigate(self, query: str) -> list[dict[str, str]]:
        """Return fake relevant notes.

        Args:
            query: Search query string.

        Returns:
            List of dicts with title, path, content keys.
        """
        return [
            {
                "title": "Main Module",
                "path": "/tmp/obsidian/entities.md",
                "content": f"Relevant to: {query}",
            },
        ]

    def update(self, note_type: str, content: str) -> Path:
        """Return fake updated note path.

        Args:
            note_type: Type of note being updated.
            content: New content (ignored in mock).

        Returns:
            Fake path to the updated note.
        """
        return Path(f"/tmp/obsidian/{note_type}.md")
