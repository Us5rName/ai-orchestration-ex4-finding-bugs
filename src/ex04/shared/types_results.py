"""Result types — provider responses, suspects, investigations, pipelines.

Defines the output structures returned by services and the SDK.
InvestigationResult is the single canonical investigation result type.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from typing import Any

from ex04.shared.types_evidence import StructuredEvidence
from ex04.shared.types_metrics import ComparisonReport, TokenMetrics


@dataclass
class ProviderResponse:
    """Response from an LLM provider call.

    Attributes:
        text: Generated text content.
        input_tokens: Tokens consumed in the request.
        output_tokens: Tokens consumed in the response.
        model: Model that generated the response.
        provider: Provider name (e.g. 'openai', 'anthropic').
        timestamp: When the response was generated.
    """

    text: str = ""
    input_tokens: int = 0
    output_tokens: int = 0
    model: str = ""
    provider: str = ""
    timestamp: datetime = field(default_factory=datetime.now)


@dataclass
class Suspect:
    """A suspect code location ranked by likelihood of containing a bug.

    Attributes:
        file_path: Source file path.
        line_start: Starting line number.
        line_end: Ending line number.
        score: Ranking score (higher = more likely).
        reason: Explanation for the ranking.
    """

    file_path: str
    line_start: int
    line_end: int
    score: float = 0.0
    reason: str = ""


@dataclass
class InvestigationResult:
    """Single canonical result of a bug investigation run.

    Core diagnosis (both modes): root_cause, suspects, proposed_fix,
    fix_applied, test_results, token_usage, original_problem, fix_diff,
    files_read.

    Run-level tracking: run_id, mode, config_hash, target_commit;
    parser_status ('not_run'|'parsed_ok'|'parse_failed'|'empty');
    diagnosis_status ('unverified'|'grounded_candidate'|'rejected');
    gate_status ('not_requested'|'not_run'|'passed'|'failed'|'blocked'|'inconclusive');
    verification_status ('unverified'|'verified'|'rejected'|'blocked');
    evidence list, limitations, telemetry_available, input/output_tokens,
    bytes_read, tool_calls, model_calls, iterations, duration_seconds,
    estimated_cost_usd, evidence_class, trace_path.
    """

    # Core diagnosis
    root_cause: str = ""
    suspects: list[Suspect] = field(default_factory=list)
    proposed_fix: str = ""
    fix_applied: bool = False
    test_results: dict[str, Any] = field(default_factory=dict)
    token_usage: TokenMetrics = field(default_factory=TokenMetrics)
    original_problem: str = ""
    fix_diff: str = ""
    files_read: int = 0
    # Run-level tracking
    run_id: str = ""
    mode: str = ""
    config_hash: str = ""
    target_commit: str = "unknown"
    parser_status: str = "not_run"
    diagnosis_status: str = "unverified"
    gate_status: str = "not_requested"
    verification_status: str = "unverified"
    evidence: list[StructuredEvidence] = field(default_factory=list)
    limitations: list[str] = field(default_factory=list)
    telemetry_available: bool = False
    input_tokens: int | None = None
    output_tokens: int | None = None
    context_tokens: int = 0
    bytes_read: int = 0
    tool_calls: int = 0
    model_calls: int = 0
    iterations: int = 0
    retries: int = 0
    duration_seconds: float = 0.0
    estimated_cost_usd: float | None = None
    evidence_class: str = "fixture"
    trace_path: str = ""
    trace_hash: str = ""


@dataclass
class PipelineResult:
    """Result of the full end-to-end pipeline execution.

    Attributes:
        graph_result: Path to generated graph data.
        vault_result: Path to generated vault.
        investigation: Bug investigation findings.
        comparison: Token comparison report.
        engineering: Reverse engineering results.
        bug_report_md: Structured Markdown bug report from the investigation.
    """

    graph_result: str = ""
    vault_result: str = ""
    investigation: InvestigationResult = field(default_factory=InvestigationResult)
    comparison: ComparisonReport = field(default_factory=ComparisonReport)
    engineering: str = ""
    bug_report_md: str = ""
