"""Vault Builder helpers — markdown content generation utilities.

Extracted from builder.py to keep the main module under 150 lines.
Provides functions for generating entity notes, index, and hot area
markdown content for Obsidian vaults.

Implementation: **Phase 4** (T4.04, extracted)
"""

from __future__ import annotations

from datetime import datetime

from ex04.services.vault.sanitize import safe_name, yaml_double_quote
from ex04.shared.types import Community, Entity, GraphData


def build_entity_content(
    entity: Entity,
    relations: dict[str, list[str]],
    entity_names: set[str],
) -> str:
    """Build markdown content for a single entity note.

    Args:
        entity: The entity to write a note for.
        relations: Map of entity names to related entity names.
        entity_names: Set of all entity names for wikilink resolution.

    Returns:
        Markdown content string for the entity note.
    """
    lines: list[str] = []
    lines.append("---")
    lines.append(f"title: {yaml_double_quote(entity.name)}")
    lines.append(f"tags: [entity, {entity.kind}]")
    lines.append(f"date: {datetime.now().strftime('%Y-%m-%d')}")
    lines.append("---")
    lines.append("")
    lines.append(f"# {entity.name}")
    lines.append("")
    lines.append("## Properties")
    lines.append(f"- **Kind**: {entity.kind}")
    if entity.file_path:
        lines.append(f"- **File**: {entity.file_path}")
    if entity.line_range != (0, 0):
        start, end = entity.line_range
        lines.append(f"- **Lines**: {start}–{end}")
    lines.append("")

    related = relations.get(entity.name, [])
    if related:
        lines.append("## Related")
        for target in related:
            if target in entity_names:
                lines.append(f"- [[{safe_name(target)}]]")
        lines.append("")

    return "\n".join(lines)


def build_index_content(graph_data: GraphData) -> str:
    """Build markdown content for the vault index.md.

    Args:
        graph_data: Graph data for generating navigation.

    Returns:
        Markdown content string for the index.
    """
    lines: list[str] = []
    lines.append("# Graph Index")
    lines.append("")
    lines.append("Auto-generated from graph analysis.")
    lines.append("")

    lines.append("## Entities")
    for entity in graph_data.entities:
        lines.append(f"- [[notes/{safe_name(entity.name)}|{entity.name}]] ({entity.kind})")
    lines.append("")

    if graph_data.relationships:
        lines.append("## Relationships")
        for rel in graph_data.relationships:
            lines.append(f"- {rel.source} --[{rel.type}]--> {rel.target}")
        lines.append("")

    if graph_data.communities:
        lines.append("## Communities")
        for comm in graph_data.communities:
            lines.extend(_build_community_section(comm))
        lines.append("")

    return "\n".join(lines)


def _build_community_section(comm: Community) -> list[str]:
    """Build markdown lines for a single community section.

    Args:
        comm: The community to render.

    Returns:
        List of markdown lines for this community.
    """
    lines: list[str] = []
    lines.append(f"### {comm.name}")
    for ent in comm.entities:
        lines.append(f"- [[notes/{safe_name(ent)}|{ent}]]")
    lines.append("")
    return lines


def build_hot_content(graph_data: GraphData) -> str:
    """Build markdown content for the vault hot.md.

    Args:
        graph_data: Graph data for generating hot area content.

    Returns:
        Markdown content string for the hot area.
    """
    lines: list[str] = []
    lines.append("# Hot Area")
    lines.append("")
    lines.append("Auto-generated bug focus area.")
    lines.append("")

    if graph_data.communities:
        largest = max(graph_data.communities, key=lambda c: c.size)
        lines.append(f"## Primary Focus: {largest.name}")
        lines.append("Entities in this community:")
        for ent in largest.entities:
            lines.append(f"- [[notes/{safe_name(ent)}|{ent}]]")
        lines.append("")

    file_entities = [e for e in graph_data.entities if e.kind == "file"]
    if file_entities:
        lines.append("## Source Files")
        for ent in file_entities:
            lines.append(f"- [[notes/{safe_name(ent.name)}|{ent.name}]]")
        lines.append("")

    return "\n".join(lines)
