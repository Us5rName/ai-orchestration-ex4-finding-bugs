"""Graph and vault context builders for GraphGuidedRunner.

Extracted to keep graph_guided_runner.py under 150 lines (DRY).

Traceability: [TODO P6-R04-ext]
"""

from __future__ import annotations

from pathlib import Path

from ex04.services.comparison.ranking import rank_entities
from ex04.shared.types import GraphData
from ex04.shared.types_evidence import StructuredEvidence

_MAX_ENTITIES = 20
_MAX_VAULT_NOTES = 3


def build_graph_context(
    graph_data: GraphData | None,
    bug_report: str,
    evidence: list[StructuredEvidence],
) -> tuple[str, list[str], list[str]]:
    """Build multi-signal ranked entity context; populate evidence in-place.

    Returns:
        (context_text, source_anchors, limitations).
    """
    if graph_data is None:
        return "Graph: unavailable", [], ["Graph data not provided."]

    ranked = rank_entities(
        graph_data.entities, graph_data.relationships, bug_report, _MAX_ENTITIES
    )
    anchors: list[str] = []
    lines = ["Graph entities (multi-signal ranked):"]
    missing = 0

    for entity, score in ranked:
        if entity.file_path:
            anchor = f"{entity.file_path}:{entity.line_range[0]}-{entity.line_range[1]}"
            anchors.append(anchor)
        else:
            anchor = "unknown"
            missing += 1
        evidence.append(StructuredEvidence(
            source_file=entity.file_path,
            line_start=entity.line_range[0],
            line_end=entity.line_range[1],
            symbol=entity.name,
            graph_node=entity.name,
            ranking_score=score,
            sent_to_model=True,
        ))
        lines.append(f"  - {entity.name} [{entity.kind}] score={score:.2f} anchor={anchor}")

    for rel in graph_data.relationships[:15]:
        lines.append(f"  {rel.source} --{rel.type}--> {rel.target}")

    lims = [f"{missing} entities lack a valid source anchor."] if missing else []
    return "\n".join(lines), anchors, lims


def build_vault_context(
    vault_path: Path | None,
    evidence: list[StructuredEvidence],
) -> tuple[str, int, list[str]]:
    """Navigate vault; record each note as StructuredEvidence in-place.

    Returns:
        (context_text, files_read, limitations).
    """
    if vault_path is None or not vault_path.is_dir():
        return "Vault: unavailable", 0, []
    candidates = [vault_path / "index.md", vault_path / "hot.md"]
    notes = [p for p in candidates if p.is_file()][:_MAX_VAULT_NOTES]
    if not notes:
        return "Vault: no index or hot notes found", 0, []
    text = "\n\n".join(
        f"=== {n.name} ===\n{n.read_text(encoding='utf-8')}" for n in notes
    )
    for note in notes:
        evidence.append(StructuredEvidence(vault_note=note.name, sent_to_model=True))
    return text, len(notes), []
