"""Reverse Engineer — reverse engineers code structure from graph data.

Generates Mermaid diagrams and architectural summaries from parsed GraphData,
including block diagrams, OOP class diagrams, and pattern detection.

## Contract (AnalysisServiceInterface)

| Method | Input | Output | Phase |
|---|---|---|---|
| `reverse_engineer(graph_data)` | GraphData | str | P4 |

Implementation: **Phase 4** (T4.16)
"""

from __future__ import annotations

import logging

from ex04.services.analysis.reverse_engineer_helpers import (
    build_block_diagram_lines,
    build_class_diagram_lines,
)
from ex04.services.analysis.reverse_engineer_text import (
    build_communities_section,
    build_entity_summary,
    build_relationships_section,
    identify_patterns,
)
from ex04.shared.types import GraphData

logger = logging.getLogger(__name__)


class ReverseEngineer:
    """Reverse engineers architecture from graph data.

    Generates Mermaid diagrams (block + class) and text summaries
    including entity counts, relationships, communities, and patterns.

    Attributes:
        graph_data: Parsed graph data to analyze.
    """

    def __init__(self) -> None:
        """Initialize the reverse engineer."""
        self.graph_data: GraphData | None = None

    def reverse_engineer(self, graph_data: GraphData) -> str:
        """Reverse engineer architecture from graph data.

        Generates a comprehensive architectural summary including
        Mermaid block diagram, class diagram, entity summary,
        relationships, communities, and detected patterns.

        Args:
            graph_data: Parsed graph data to analyze.

        Returns:
            Human-readable architectural summary with Mermaid diagrams.
        """
        self.graph_data = graph_data
        sections: list[str] = []

        sections.append("# Architecture Analysis")
        sections.append("")
        sections.append("## Overview")
        sections.append(f"- **Entities**: {len(graph_data.entities)}")
        sections.append(f"- **Relationships**: {len(graph_data.relationships)}")
        sections.append(f"- **Communities**: {len(graph_data.communities)}")
        sections.append("")

        sections.append("## Block Diagram")
        sections.append("")
        sections.append("```mermaid")
        sections.append("block")
        sections.extend(build_block_diagram_lines(graph_data))
        sections.append("```\n")

        sections.append("## OOP Schema")
        sections.append("")
        sections.append("```mermaid")
        sections.append("classDiagram")
        sections.extend(build_class_diagram_lines(graph_data))
        sections.append("```\n")

        sections.append("## Entity Summary")
        sections.extend(build_entity_summary(graph_data))
        sections.append("")

        sections.append("## Relationships")
        sections.extend(build_relationships_section(graph_data))
        sections.append("")

        if graph_data.communities:
            sections.append("## Communities")
            sections.extend(build_communities_section(graph_data.communities))
            sections.append("")

        sections.append("## Patterns")
        sections.extend(identify_patterns(graph_data))
        sections.append("")

        return "\n".join(sections)

    def extract_block_schema(self, graph_data: GraphData) -> str:
        """Extract a Mermaid block diagram from graph data.

        Groups entities by source file and draws blocks with
        relationships between them.

        Args:
            graph_data: Parsed graph data.

        Returns:
            Mermaid block diagram string.
        """
        lines: list[str] = ["```mermaid", "block"]
        lines.extend(build_block_diagram_lines(graph_data))
        lines.append("```")
        return "\n".join(lines)

    def extract_oop_schema(self, graph_data: GraphData) -> str:
        """Extract a Mermaid class diagram from graph data.

        Shows classes and inheritance/usage relationships.

        Args:
            graph_data: Parsed graph data.

        Returns:
            Mermaid class diagram string.
        """
        lines: list[str] = ["```mermaid", "classDiagram"]
        lines.extend(build_class_diagram_lines(graph_data))
        lines.append("```")
        return "\n".join(lines)
