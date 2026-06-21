"""Validation helpers for comparison requests."""

from __future__ import annotations

from pathlib import PurePath
from typing import Protocol

from ex04.shared.types_request_meta import (
    EVIDENCE_CLASSES,
    LIVE_PROVIDERS,
    POLICY_NAMES,
    SHA_RE,
)


class RequestLike(Protocol):
    """Subset of ComparisonRequest needed by validators."""

    evidence_class: str
    target_commit: str
    provider: str
    model: str
    temperature: float
    gate_enabled: bool
    reproduction_command: str
    gate_reproduction_command: str
    expected_failure_signature: str
    artifact_root: str
    patch_enabled: bool
    patch_allowed_paths: list[str]
    gate_policy_checks: list[str]


def validate_identity_and_provider(req: RequestLike) -> None:
    """Validate evidence class, target identity, and provider settings."""
    if req.evidence_class not in EVIDENCE_CLASSES:
        raise ValueError(f"invalid evidence_class: {req.evidence_class}")
    if req.evidence_class != "fixture" and req.target_commit == "unknown":
        raise ValueError("target_commit must be pinned for non-fixture runs")
    if req.evidence_class == "live" and (
        req.provider not in LIVE_PROVIDERS or not req.model.strip()
    ):
        raise ValueError("live runs require supported provider and model")
    if not 0 <= req.temperature <= 2:
        raise ValueError("temperature must be between 0 and 2")


def validate_gate_inputs(req: RequestLike) -> None:
    """Validate gate-specific input consistency."""
    if req.gate_enabled and not (req.reproduction_command or req.gate_reproduction_command):
        raise ValueError("reproduction command required when gate is enabled")
    if (req.gate_enabled and req.evidence_class == "deterministic"
            and not req.expected_failure_signature.strip()):
        raise ValueError("expected_failure_signature required for deterministic gate")


def validate_paths_and_patch(req: RequestLike) -> None:
    """Validate safe paths and patch/gate setting consistency."""
    root = PurePath(req.artifact_root)
    if root.is_absolute() or ".." in root.parts:
        raise ValueError("artifact_root must be a safe relative path")
    if req.target_commit != "unknown" and not SHA_RE.match(req.target_commit):
        raise ValueError("target_commit must be a full hex commit hash")
    if req.gate_enabled and not req.patch_enabled:
        raise ValueError("gate_enabled requires patch_enabled")
    if req.patch_enabled and not req.patch_allowed_paths:
        raise ValueError("patch_enabled requires patch_allowed_paths")


def validate_policies(req: RequestLike) -> None:
    """Validate duplicate or unknown gate policy names."""
    if len(req.gate_policy_checks) != len(set(req.gate_policy_checks)):
        raise ValueError("duplicate gate policy checks")
    invalid = [p for p in req.gate_policy_checks if p not in POLICY_NAMES]
    if invalid:
        raise ValueError(f"invalid gate policy checks: {invalid}")
