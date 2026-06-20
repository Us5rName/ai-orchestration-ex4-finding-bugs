"""Reverse Engineer helpers — text summary generation utilities.

Extracted from reverse_engineer.py to keep the main module under 150 lines.
Provides functions for building entity summaries, relationship sections,
community sections, and pattern detection.

Implementation: **Phase 4** (T4.16, extracted)
"""

from __future__ import annotations

from collections import defaultdict

from ex04.shared.types import Community, GraphData


def build_entity_summary(graph_data: GraphData) -> list[str]:
    """Build entity summary section.

    Args:
        graph_data: Parsed graph data.

    Returns:
        List of markdown lines for entity summary.
    """
    lines: list[str] = []
    kind_counts: dict[str, int] = defaultdict(int)
    for entity in graph_data.entities:
        kind_counts[entity.kind] += 1
    for kind, count in sorted(kind_counts.items()):
        lines.append(f"- **{kind}**: {count}")
    return lines


def build_relationships_section(graph_data: GraphData) -> list[str]:
    """Build relationships section.

    Args:
        graph_data: Parsed graph data.

    Returns:
        List of markdown lines for relationships.
    """
    lines: list[str] = []
    type_counts: dict[str, int] = defaultdict(int)
    for rel in graph_data.relationships:
        type_counts[rel.type] += 1
    if not type_counts:
        lines.append("- No relationships detected")
        return lines
    for rel_type, count in sorted(type_counts.items()):
        lines.append(f"- **{rel_type}**: {count}")
    return lines


def build_communities_section(communities: list[Community]) -> list[str]:
    """Build communities section.

    Args:
        communities: List of communities to render.

    Returns:
        List of markdown lines for communities.
    """
    return [f"- **{comm.name}**: {comm.size} entities" for comm in communities]


def identify_patterns(graph_data: GraphData) -> list[str]:
    """Identify common design patterns in the graph.

    Args:
        graph_data: Parsed graph data.

    Returns:
        List of markdown lines describing detected patterns.
    """
    lines: list[str] = []
    classes = [e for e in graph_data.entities if e.kind == "class"]

    inheritances = [r for r in graph_data.relationships if r.type == "inherits"]
    if inheritances:
        lines.append(
            f"- **Inheritance Hierarchy**: Detected {len(inheritances)} inheritance relationship(s)"
        )

    repo_classes = [
        e for e in classes if "repo" in e.name.lower() or "repository" in e.name.lower()
    ]
    if len(repo_classes) >= 2:
        lines.append(f"- **Repository Pattern**: Found {len(repo_classes)} repository class(es)")

    incoming: dict[str, int] = defaultdict(int)
    for rel in graph_data.relationships:
        incoming[rel.target] += 1
    for target, count in incoming.items():
        if count >= 3:
            lines.append(f"- **Central Component**: {target} has {count} incoming relationships")

    if not lines:
        lines.append("- No distinct patterns detected")
    return lines
