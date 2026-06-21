"""Experiment-specific types for Phase 6–8 controlled comparison.

Defines RunManifest, GateOutput, InvestigationRunResult, and ExperimentConfig.
These supplement the existing types_metrics and types_results without replacing them.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime

from ex04.shared.types_results import InvestigationResult


@dataclass
class ExperimentConfig:
    """Shared configuration for both comparison modes (fairness invariant).

    Both naive and graph-guided runs must receive identical values for all
    fields below. Any divergence is a fairness violation.
    """

    bug_report: str = ""
    provider: str = ""
    model: str = ""
    system_prompt: str = ""
    max_model_calls: int = 5
    max_tool_calls: int = 10
    max_iterations: int = 3
    token_budget: int = 8000
    prompt_version: str = "P6-CMP-01 v1.0"


@dataclass
class GateOutput:
    """Output from the deterministic correctness gate.

    Each field records a distinct verification step.
    """

    failure_reproduced: bool = False
    patch_applied: bool = False
    targeted_test_passed: bool | None = None
    relevant_suite_passed: bool | None = None
    prohibited_files_clean: bool = True
    tests_not_deleted: bool = True
    assertions_not_weakened: bool = True
    final_verdict: str = "skipped"
    limitations: list[str] = field(default_factory=list)
    evidence_class: str = "fixture"


@dataclass
class RunManifest:
    """Complete provenance record for one investigation run."""

    run_id: str = ""
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())
    mode: str = ""
    provider: str = ""
    model: str = ""
    model_params: dict[str, object] = field(default_factory=dict)
    config_hash: str = ""
    prompt_version: str = ""
    target_identifier: str = ""
    target_commit: str = "unknown"
    target_snapshot_hash: str = ""
    input_tokens: int | None = None
    output_tokens: int | None = None
    total_tokens: int | None = None
    estimated_cost_usd: float | None = None
    model_calls: int = 0
    tool_calls: int = 0
    files_read: int = 0
    bytes_read: int = 0
    source_anchors: list[str] = field(default_factory=list)
    iterations: int = 0
    duration_seconds: float = 0.0
    diagnosis_status: str = ""
    patch_status: str = "not_applied"
    correctness_gate_status: str = "skipped"
    limitations: list[str] = field(default_factory=list)
    telemetry_available: bool = False
    evidence_class: str = "fixture"


@dataclass
class SignedMetrics:
    """Signed deltas between naive and graph-guided runs.

    Negative values indicate the graph-guided run performed worse on that metric.
    These must not be clamped to zero — a regression is valid evidence.
    """

    naive_tokens: int | None = None
    guided_tokens: int | None = None
    token_delta: int | None = None
    token_savings_pct: float | None = None
    naive_files: int = 0
    guided_files: int = 0
    file_delta: int = 0
    file_savings_pct: float | None = None
    naive_iterations: int = 0
    guided_iterations: int = 0
    iteration_delta: int = 0
    naive_duration: float = 0.0
    guided_duration: float = 0.0
    duration_delta: float = 0.0
    naive_correct: bool = False
    guided_correct: bool = False
    limitations: list[str] = field(default_factory=list)


@dataclass
class ComparisonOutcome:
    """Production comparison outcome for the canonical experiment path."""

    naive_result: InvestigationResult = field(default_factory=InvestigationResult)
    guided_result: InvestigationResult = field(default_factory=InvestigationResult)
    signed_metrics: SignedMetrics = field(default_factory=SignedMetrics)
    config_hash: str = ""
    manifest_paths: list[str] = field(default_factory=list)
    report_paths: list[str] = field(default_factory=list)
    evidence_class: str = "fixture"
    limitations: list[str] = field(default_factory=list)
