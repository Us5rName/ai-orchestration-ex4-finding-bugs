"""Vault Service Interface — contract for vault operations.

Defines the abstract base class that all vault service implementations
must follow. Enables parallel development — other modules depend only
on this interface, not on concrete implementations.

See ADR-005 for rationale.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from pathlib import Path

from ex04.shared.types import GraphData


class VaultServiceInterface(ABC):
    """Abstract interface for vault service operations.

    All vault-related operations (building, navigating, updating) must
    implement this interface. This enables dependency injection and
    mock-based testing.
    """

    @abstractmethod
    def build(self, graph_data: GraphData) -> dict[str, Path]:
        """Build an Obsidian vault from graph data.

        Args:
            graph_data: Parsed graph data to build vault from.

        Returns:
            Dict mapping note types to their file paths.
        """

    @abstractmethod
    def navigate(self, query: str) -> list[dict[str, str]]:
        """Navigate vault to find relevant context.

        Args:
            query: Bug description or search query string.

        Returns:
            List of dicts with 'title', 'path', 'content' keys.
        """

    @abstractmethod
    def update(self, note_type: str, content: str) -> Path:
        """Update or create a vault note.

        Args:
            note_type: Type of note to update (e.g. 'hot', 'index').
            content: New markdown content for the note.

        Returns:
            Path to the updated or created note file.
        """
