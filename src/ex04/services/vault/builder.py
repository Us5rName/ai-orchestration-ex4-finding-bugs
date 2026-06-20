"""Vault Builder — creates Obsidian vault from graph data.

Builds a complete Obsidian vault directory structure from parsed GraphData,
including index.md with navigation, individual entity notes with wikilinks,
and a hot.md file for the bug focus area.

## Contract (VaultServiceInterface)

| Method | Input | Output | Phase |
|---|---|---|---|
| `build(graph_data)` | GraphData | dict[str, Path] | P4 |

Implementation: **Phase 4** (T4.04)
"""

from __future__ import annotations

import logging
from pathlib import Path

from ex04.services.vault.builder_helpers import (
    build_entity_content,
    build_hot_content,
    build_index_content,
)
from ex04.services.vault.sanitize import safe_name
from ex04.shared.types import GraphData

logger = logging.getLogger(__name__)


class VaultBuilder:
    """Builds an Obsidian vault from parsed graph data.

    Creates the vault directory structure with index.md, entity notes,
    and hot.md. All inter-entity references use [[wikilinks]] syntax
    for Obsidian compatibility.

    Attributes:
        vault_path: Path where the vault will be created.
    """

    def __init__(self, vault_path: Path) -> None:
        """Initialize with the vault target directory.

        Args:
            vault_path: Directory path where the vault will be created.
        """
        self.vault_path = vault_path

    def build(self, graph_data: GraphData) -> dict[str, Path]:
        """Build an Obsidian vault from graph data.

        Creates the vault directory structure, index.md, entity notes,
        and hot.md. Returns a dict mapping note types to their paths.

        Args:
            graph_data: Parsed graph data to build vault from.

        Returns:
            Dict mapping note types ('index', 'hot', 'notes') to paths.
        """
        self.vault_path.mkdir(parents=True, exist_ok=True)
        notes_dir = self.vault_path / "notes"
        notes_dir.mkdir(parents=True, exist_ok=True)

        self._create_entity_notes(graph_data, notes_dir)
        index_path = self._write_file("index.md", build_index_content(graph_data))
        hot_path = self._write_file("hot.md", build_hot_content(graph_data))

        return {"index": index_path, "hot": hot_path, "notes": notes_dir}

    def _create_entity_notes(self, graph_data: GraphData, notes_dir: Path) -> list[Path]:
        """Create individual markdown notes for each entity.

        Args:
            graph_data: Graph data containing entities and relationships.
            notes_dir: Directory to write entity notes into.

        Returns:
            List of created note file paths.
        """
        entity_names = {e.name for e in graph_data.entities}
        relations: dict[str, list[str]] = {}
        for rel in graph_data.relationships:
            relations.setdefault(rel.source, []).append(rel.target)

        created: list[Path] = []
        for entity in graph_data.entities:
            note_path = notes_dir / f"{safe_name(entity.name)}.md"
            content = build_entity_content(entity, relations, entity_names)
            note_path.write_text(content, encoding="utf-8")
            created.append(note_path)
            logger.debug("Created entity note: %s", note_path)

        return created

    def _write_file(self, name: str, content: str) -> Path:
        """Write content to a file in the vault root.

        Args:
            name: Filename to create.
            content: Markdown content to write.

        Returns:
            Path to the created file.
        """
        path = self.vault_path / name
        path.write_text(content, encoding="utf-8")
        logger.info("Created vault file: %s", path)
        return path
