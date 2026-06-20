"""ComparisonRequest — full controlled-experiment contract for Phase 6–8.

Carries all controlled variables for a paired naive/graph-guided experiment.
Both modes receive identical values for every field except `mode`.

Traceability: [PRD-CE §Contract], [TODO P6-R01]
"""

from __future__ import annotations

from dataclasses import dataclass, field


@dataclass
class ComparisonRequest:
    """Complete contract for one comparison experiment.

    Groups fields into seven configuration domains so fairness enforcement
    can verify equality of every controlled variable before any provider call.
    """

    # -- Target identity -------------------------------------------------------
    target_repo: str = ""
    target_commit: str = "unknown"
    target_snapshot_hash: str = "unknown"
    bug_id: str = ""
    bug_report: str = ""
    reproduction_command: str = ""
    expected_failure_signature: str = ""

    # -- Provider configuration ------------------------------------------------
    provider: str = ""
    model: str = ""
    temperature: float = 0.0
    seed: int | None = None
    max_output_tokens: int = 4096
    provider_timeout: int = 60

    # -- Prompt configuration --------------------------------------------------
    system_prompt: str = ""
    prompt_version: str = "unknown"
    schema_version: str = "1.0"
    parser_version: str = "1.0"

    # -- Budget configuration --------------------------------------------------
    max_files: int = 20
    max_bytes: int = 524288
    token_budget: int = 8000
    max_tool_calls: int = 10
    max_model_calls: int = 5
    max_iterations: int = 3
    timeout_seconds: int = 120

    # -- Patch configuration ---------------------------------------------------
    patch_enabled: bool = False
    patch_allowed_paths: list[str] = field(default_factory=list)
    patch_prohibited_paths: list[str] = field(default_factory=list)

    # -- Gate configuration ----------------------------------------------------
    gate_reproduction_command: str = ""
    gate_verification_commands: list[str] = field(default_factory=list)
    gate_policy_checks: list[str] = field(
        default_factory=lambda: [
            "prohibited_files_clean",
            "tests_not_deleted",
            "assertions_not_weakened",
        ]
    )

    # -- Artifact / provenance configuration -----------------------------------
    run_id: str = ""
    artifact_root: str = "artifacts"
    manifest_version: str = "1.0"
    pricing_version: str = "unknown"
    fixture_class: str = "fixture"

    def validate(self) -> None:
        """Raise ValueError if any required field is invalid.

        Checks: non-empty required strings, positive budget values, non-empty
        provider and run_id when a live run is expected.
        """
        if not self.bug_report.strip():
            raise ValueError("bug_report must not be empty")
        if not self.provider.strip():
            raise ValueError("provider must not be empty")
        if not self.run_id.strip():
            raise ValueError("run_id must not be empty")
        for name, value in [
            ("max_files", self.max_files),
            ("max_bytes", self.max_bytes),
            ("token_budget", self.token_budget),
            ("max_tool_calls", self.max_tool_calls),
            ("max_model_calls", self.max_model_calls),
            ("max_iterations", self.max_iterations),
            ("timeout_seconds", self.timeout_seconds),
            ("max_output_tokens", self.max_output_tokens),
        ]:
            if value <= 0:
                raise ValueError(f"{name} must be positive, got {value}")
