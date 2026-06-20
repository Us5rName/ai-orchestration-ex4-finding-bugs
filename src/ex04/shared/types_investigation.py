"""Structured evidence and investigation run record types for Phase 6–8.

These types carry the full evidence trail for one investigation run.
They accompany InvestigationResult without replacing it.

Traceability: [PRD-CE §Result Contract], [TODO P6-R02]
"""

from __future__ import annotations

from dataclasses import dataclass, field


@dataclass
class StructuredEvidence:
    """One piece of structured evidence in an investigation run.

    Represents a source anchor, graph node, vault note, or combination
    that influenced the diagnosis. Missing anchors must be represented
    explicitly (empty string) rather than omitted.
    """

    source_file: str = ""
    line_start: int = 0
    line_end: int = 0
    symbol: str = ""
    excerpt_hash: str = ""
    graph_node: str = ""
    edge_type: str = ""
    vault_note: str = ""
    ranking_score: float = 0.0
    sent_to_model: bool = False
    in_final_diagnosis: bool = False


@dataclass
class InvestigationRunRecord:
    """Telemetry and evidence record for one bounded investigation run.

    Carries run-level metadata, telemetry, and a list of StructuredEvidence
    entries. Produced by both NaiveRunner and GraphGuidedRunner alongside
    their RunMetrics. Evidence class must be set by the producing runner.
    """

    run_id: str = ""
    mode: str = ""
    target_commit: str = "unknown"
    config_hash: str = ""
    parser_status: str = "not_run"
    gate_status: str = "not_run"
    limitations: list[str] = field(default_factory=list)
    telemetry_available: bool = False
    input_tokens: int | None = None
    output_tokens: int | None = None
    bytes_read: int = 0
    tool_calls: int = 0
    model_calls: int = 0
    iterations: int = 0
    duration_seconds: float = 0.0
    estimated_cost_usd: float | None = None
    evidence: list[StructuredEvidence] = field(default_factory=list)
    evidence_class: str = "fixture"
    trace: list[dict[str, object]] = field(default_factory=list)
