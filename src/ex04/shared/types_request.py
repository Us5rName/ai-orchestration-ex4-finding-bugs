"""Canonical request contract for controlled comparison experiments."""

from __future__ import annotations

import hashlib
import json
from dataclasses import asdict, dataclass, field, fields

from ex04.shared.types_request_meta import (
    CONTROLLED,
    FAIRNESS_CLASSES,
    INFORMATIONAL,
    MODE_SPECIFIC,
    dict_field,
    list_field,
    request_field,
)
from ex04.shared.types_request_validation import (
    validate_gate_inputs,
    validate_identity_and_provider,
    validate_paths_and_patch,
    validate_policies,
)


@dataclass
class ComparisonRequest:
    """Authoritative input contract for one bounded comparison experiment."""

    target_repo: str = request_field()
    target_commit: str = request_field("unknown")
    target_snapshot_hash: str = request_field("unknown")
    bug_id: str = request_field()
    bug_report: str = request_field()
    reproduction_command: str = request_field()
    expected_failure_signature: str = request_field()
    target_snapshot_path: str = request_field()
    provider: str = request_field()
    model: str = request_field()
    temperature: float = request_field(0.0)
    seed: int | None = request_field(None)
    max_output_tokens: int = request_field(4096)
    provider_timeout: int = request_field(60)
    retry_limit: int = request_field(0)
    model_params: dict[str, object] = dict_field()
    system_prompt: str = request_field()
    prompt_version: str = request_field("unknown")
    schema_version: str = request_field("1.0")
    parser_version: str = request_field("1.0")
    output_schema_id: str = request_field("ex04.investigation.v1")
    max_files: int = request_field(20)
    max_bytes: int = request_field(524288)
    token_budget: int = request_field(8000)
    max_tool_calls: int = request_field(10)
    max_model_calls: int = request_field(5)
    max_iterations: int = request_field(3)
    max_retries: int = request_field(0)
    timeout_seconds: int = request_field(120)
    patch_enabled: bool = request_field(False)
    patch_allowed_paths: list[str] = list_field()
    patch_prohibited_paths: list[str] = list_field()
    max_changed_files: int = request_field(10)
    max_patch_bytes: int = request_field(65536)
    generated_path_patterns: list[str] = list_field()
    vendor_path_patterns: list[str] = list_field()
    gate_enabled: bool = request_field(False)
    gate_reproduction_command: str = request_field()
    gate_verification_commands: list[str] = list_field()
    gate_policy_checks: list[str] = field(
        default_factory=lambda: [
            "prohibited_files_clean", "tests_not_deleted", "assertions_not_weakened",
        ],
        metadata={"fairness": CONTROLLED},
    )
    require_diagnosis_consistency: bool = request_field(False)
    run_id: str = request_field("", MODE_SPECIFIC)
    mode: str = request_field("", MODE_SPECIFIC)
    strategy_artifact_dir: str = request_field("", MODE_SPECIFIC)
    artifact_root: str = request_field("artifacts")
    manifest_version: str = request_field("1.0")
    pricing_version: str = request_field("unknown")
    evidence_class: str = request_field("fixture")
    repo_commit: str = request_field("unknown")
    fixture_class: str = request_field("fixture", INFORMATIONAL)

    def validate(self) -> None:
        """Raise ValueError if the request cannot run truthfully or safely."""
        for name in ("bug_report", "provider", "run_id"):
            if not str(getattr(self, name)).strip():
                raise ValueError(f"{name} must not be empty")
        validate_identity_and_provider(self)
        self._validate_limits()
        if self.retry_limit < 0 or self.max_retries < 0:
            raise ValueError("retry limits must be non-negative")
        validate_gate_inputs(self)
        validate_paths_and_patch(self)
        validate_policies(self)

    def controlled_payload(self) -> dict[str, object]:
        """Return all fields classified as controlled, in stable key order."""
        data = asdict(self)
        return {f.name: data[f.name] for f in fields(self) if fairness_of(f.name) == CONTROLLED}

    def controlled_config_hash(self) -> str:
        """Return full SHA-256 digest of the controlled payload."""
        payload = json.dumps(self.controlled_payload(), sort_keys=True, default=str)
        return hashlib.sha256(payload.encode()).hexdigest()

    def _validate_limits(self) -> None:
        for name in ("max_files", "max_bytes", "token_budget", "max_tool_calls",
                     "max_model_calls", "max_iterations", "timeout_seconds",
                     "max_output_tokens", "provider_timeout", "max_changed_files",
                     "max_patch_bytes"):
            if int(getattr(self, name)) <= 0:
                raise ValueError(f"{name} must be positive, got {getattr(self, name)}")

def fairness_of(name: str) -> str:
    """Return fairness classification for a ComparisonRequest field."""
    for item in fields(ComparisonRequest):
        if item.name == name:
            value = item.metadata.get("fairness")
            if value not in FAIRNESS_CLASSES:
                raise ValueError(f"missing fairness classification for {name}")
            return str(value)
    raise KeyError(name)


def classified_field_names(kind: str) -> list[str]:
    """Return field names with the requested fairness classification."""
    return [f.name for f in fields(ComparisonRequest) if fairness_of(f.name) == kind]
