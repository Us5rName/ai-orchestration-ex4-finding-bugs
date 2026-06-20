"""Reverse Engineer helpers — diagram generation and enrichment utilities.

Extracted from reverse_engineer.py to keep the main module under 150 lines.
Provides functions for building Mermaid block and class diagrams, and a
gatekeeper-assisted LLM enrichment helper.

Implementation: **Phase 4** (T4.16, extracted)
"""

from __future__ import annotations

from collections import defaultdict

from ex04.shared.gatekeeper import GatekeeperInterface
from ex04.shared.types import GraphData


def build_block_diagram_lines(graph_data: GraphData) -> list[str]:
    """Build Mermaid block diagram lines grouped by source file.

    Args:
        graph_data: Parsed graph data.

    Returns:
        List of Mermaid block diagram lines.
    """
    lines: list[str] = []
    file_groups: dict[str, list[str]] = defaultdict(list)

    for entity in graph_data.entities:
        file_key = entity.file_path or "unknown"
        file_groups[file_key].append(entity.name)

    for file_key, entities in sorted(file_groups.items()):
        safe_name = file_key.replace(".", "_").replace("/", "_")
        lines.append(f'  id"{safe_name}" [{file_key}]')
        for entity in entities:
            safe_ent = entity.replace(" ", "_")
            lines.append(f'  id"{safe_ent}" [{entity}]')

    for rel in graph_data.relationships:
        src_safe = rel.source.replace(" ", "_")
        tgt_safe = rel.target.replace(" ", "_")
        lines.append(f"  {src_safe} --> {tgt_safe}")

    return lines


def build_class_diagram_lines(graph_data: GraphData) -> list[str]:
    """Build Mermaid class diagram lines.

    Args:
        graph_data: Parsed graph data.

    Returns:
        List of Mermaid class diagram lines.
    """
    lines: list[str] = []

    for entity in graph_data.entities:
        if entity.kind == "class":
            lines.append(f"  class {entity.name} {{}}")

    for rel in graph_data.relationships:
        if rel.type == "inherits":
            lines.append(f"  {rel.target} <|-- {rel.source}")
        else:
            lines.append(f"  {rel.source} --> {rel.target}")

    return lines


def enrich_with_llm(summary: str, gatekeeper: GatekeeperInterface, provider: str) -> str:
    """Append LLM-generated architectural insights to an architecture summary.

    Sends the draft summary to the LLM via the gatekeeper and appends
    the response as a '## LLM Insights' section. Returns the original
    summary unchanged if the LLM returns an empty response.

    Args:
        summary: Draft architecture summary to enrich.
        gatekeeper: Gatekeeper instance for routing the LLM call.
        provider: LLM provider name (e.g. 'openai', 'anthropic').

    Returns:
        Enriched summary string with an appended LLM Insights section,
        or the original summary if the LLM response is empty.
    """
    prompt = (
        "You are a software architect. Review the following architectural summary "
        "and provide brief additional insights about design quality, coupling, "
        "or potential improvements (3-5 bullet points).\n\n"
        f"{summary}"
    )
    response = gatekeeper.send(provider, [{"role": "user", "content": prompt}])
    insights = response.text.strip()
    if not insights:
        return summary
    return f"{summary}\n## LLM Insights\n\n{insights}\n"
