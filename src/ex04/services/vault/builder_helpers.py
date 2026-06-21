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


def _note_link(name: str, label: str | None = None) -> str:
    text = label or name
    return f"[[notes/{safe_name(name)}|{text}]]"


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
    lines = [
        "---",
        f"title: {yaml_double_quote(entity.name)}",
        f"tags: [entity, {entity.kind}]",
        f"date: {datetime.now().strftime('%Y-%m-%d')}",
        "---",
        "",
        f"# {entity.name}",
        "",
        "## Properties",
        f"- **Kind**: {entity.kind}",
    ]
    if entity.file_path:
        lines.append(f"- **File**: {entity.file_path}")
    if entity.line_range != (0, 0):
        start, end = entity.line_range
        lines.append(f"- **Lines**: {start}–{end}")
    lines.append("")

    related = relations.get(entity.name, [])
    if related:
        lines.extend(["## Related", *(_related_links(related, entity_names)), ""])

    return "\n".join(lines)


def _related_links(related: list[str], entity_names: set[str]) -> list[str]:
    return [f"- [[{safe_name(target)}]]" for target in related if target in entity_names]


def build_index_content(graph_data: GraphData) -> str:
    """Build markdown content for the vault index.md.

    Args:
        graph_data: Graph data for generating navigation.

    Returns:
        Markdown content string for the index.
    """
    lines = [
        "# Graph Index",
        "",
        "Auto-generated from graph analysis.",
        "",
        "## Entities",
        *(f"- {_note_link(entity.name)} ({entity.kind})" for entity in graph_data.entities),
        "",
    ]

    if graph_data.relationships:
        rel_lines = [
            f"- {rel.source} --[{rel.type}]--> {rel.target}"
            for rel in graph_data.relationships
        ]
        lines.extend(
            [
                "## Relationships",
                *rel_lines,
                "",
            ]
        )

    if graph_data.communities:
        community_lines = [
            line
            for comm in graph_data.communities
            for line in _build_community_section(comm)
        ]
        lines.extend(["## Communities", *community_lines, ""])

    return "\n".join(lines)


def _build_community_section(comm: Community) -> list[str]:
    """Build markdown lines for a single community section.

    Args:
        comm: The community to render.

    Returns:
        List of markdown lines for this community.
    """
    return [f"### {comm.name}", *[f"- {_note_link(ent)}" for ent in comm.entities], ""]


def build_hot_content(graph_data: GraphData) -> str:
    """Build markdown content for the vault hot.md.

    Args:
        graph_data: Graph data for generating hot area content.

    Returns:
        Markdown content string for the hot area.
    """
    lines = ["# Hot Area", "", "Auto-generated bug focus area.", ""]

    if graph_data.communities:
        largest = max(graph_data.communities, key=lambda c: c.size)
        lines.extend(
            [
                f"## Primary Focus: {largest.name}",
                "Entities in this community:",
                *[f"- {_note_link(ent)}" for ent in largest.entities],
                "",
            ]
        )

    file_entities = [e for e in graph_data.entities if e.kind == "file"]
    if file_entities:
        lines.extend(
            [
                "## Source Files",
                *(f"- {_note_link(entity.name)}" for entity in file_entities),
                "",
            ]
        )

    return "\n".join(lines)
