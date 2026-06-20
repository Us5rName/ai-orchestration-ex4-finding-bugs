"""Budgeted graph/vault context operations for graph-guided runner."""

from __future__ import annotations

import hashlib
from pathlib import Path

from ex04.services.comparison.budget import BudgetLedger, estimate_context_tokens
from ex04.services.comparison.ranking import rank_entities
from ex04.services.comparison.trace import TraceRecorder
from ex04.shared.types import GraphData
from ex04.shared.types_evidence import StructuredEvidence


def graph_context(
    graph_data: GraphData | None, bug_report: str,
    ledger: BudgetLedger, trace: TraceRecorder,
) -> tuple[str, list[StructuredEvidence], list[str]]:
    """Build ranked graph context within shared budgets."""
    if graph_data is None:
        return "Graph: unavailable", [], ["Graph data not provided."]
    evidence: list[StructuredEvidence] = []
    limitations: list[str] = []
    lines = ["Graph entities (ranked):"]
    ledger.check(tools=1)
    ledger.record(tools=1)
    trace.record("graph_query", ledger, entities=len(graph_data.entities))
    for entity, score in rank_entities(graph_data.entities, graph_data.relationships, bug_report):
        line = f"- {entity.name} [{entity.kind}] {entity.file_path}:{entity.line_range}"
        tokens = estimate_context_tokens(line)
        ledger.check(tools=1, tokens=tokens)
        ledger.record(tools=1, tokens=tokens)
        trace.record("relationship_traversal", ledger, graph_node=entity.name)
        lines.append(line)
        if not entity.file_path or entity.line_range == (0, 0):
            limitations.append(f"Graph entity lacks source anchor: {entity.name}")
        evidence.append(StructuredEvidence(
            source_file=entity.file_path, line_start=entity.line_range[0],
            line_end=entity.line_range[1], symbol=entity.name, graph_node=entity.name,
            node_type=entity.kind, ranking_score=score,
            ranking_signal_breakdown={"combined": score}, sent_to_model=True,
        ))
    for rel in graph_data.relationships[:10]:
        ledger.check(tools=1)
        ledger.record(tools=1)
        trace.record("relationship_traversal", ledger, edge_type=rel.type)
        lines.append(f"{rel.source} --{rel.type}--> {rel.target}")
    return "\n".join(lines), evidence, limitations


def vault_context(
    vault_path: Path | None, ledger: BudgetLedger, trace: TraceRecorder,
) -> tuple[str, list[StructuredEvidence], list[str]]:
    """Read bounded vault notes and record actual bytes consumed."""
    if vault_path is None or not vault_path.is_dir():
        return "Vault: unavailable", [], []
    notes = [p for p in (vault_path / "index.md", vault_path / "hot.md") if p.is_file()]
    lines: list[str] = []
    evidence: list[StructuredEvidence] = []
    for note in notes:
        text = note.read_text(encoding="utf-8", errors="replace")
        data = text.encode()
        tokens = estimate_context_tokens(text)
        ledger.check(files=1, bytes_=len(data), tokens=tokens, tools=1)
        ledger.record(files=1, bytes_=len(data), tokens=tokens, tools=1)
        trace.record("vault_note_read", ledger, path=note.name, bytes=len(data))
        lines.append(f"=== {note.name} ===\n{text}")
        evidence.append(StructuredEvidence(
            vault_note=note.name, excerpt_hash=hashlib.sha256(data).hexdigest(),
            sent_to_model=True,
        ))
    return "\n\n".join(lines) if lines else "Vault: no notes read", evidence, []
