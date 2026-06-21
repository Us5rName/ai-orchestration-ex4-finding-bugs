"""Controlled-configuration parity fingerprint for comparison experiments.

Both comparison modes must use an identical controlled configuration.
This module provides a typed ControlledConfig, a deterministic fingerprint,
and an assertion helper that must be called before any provider invocation.

Excluded from the fingerprint (treatment variables):
- API keys and secrets
- Context content and context strategy
- Mode-specific artifact paths
- Run IDs
"""

from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass

CORRECTNESS_GATE_VERSION = "1.0"
PARITY_FINGERPRINT_VERSION = "1.0"


class ParityError(Exception):
    """Raised when controlled configurations do not match before a provider call."""


@dataclass(frozen=True, slots=True)
class ControlledConfig:
    """Controlled (non-treatment) configuration for parity validation.

    All fields here are shared between naive and graph-guided modes.
    Context strategy and content are intentionally excluded — they are
    the experimental treatment variables.

    Attributes:
        provider: Provider name (e.g. "openai").
        model: Model identifier.
        temperature: Sampling temperature.
        max_tokens: Maximum output tokens.
        system_prompt_version: Version tag of the system prompt text.
        prompt_envelope_version: Version of the prompt builder envelope.
        output_schema_version: Version of the output JSON schema.
        retry_max_attempts: Provider retry limit.
        correctness_gate_version: Version of the correctness gate policy.
    """

    provider: str
    model: str
    temperature: float
    max_tokens: int
    system_prompt_version: str
    prompt_envelope_version: str
    output_schema_version: str
    retry_max_attempts: int
    correctness_gate_version: str


def compute_parity_fingerprint(config: ControlledConfig) -> str:
    """Return the deterministic SHA-256 fingerprint of a ControlledConfig.

    Uses stable key ordering and canonical JSON encoding. Safe to log
    (contains no secrets).

    Args:
        config: The controlled configuration to fingerprint.

    Returns:
        64-character lowercase hex SHA-256 digest.
    """
    payload: dict[str, object] = {
        "correctness_gate_version": config.correctness_gate_version,
        "max_tokens": config.max_tokens,
        "model": config.model,
        "output_schema_version": config.output_schema_version,
        "prompt_envelope_version": config.prompt_envelope_version,
        "provider": config.provider,
        "retry_max_attempts": config.retry_max_attempts,
        "system_prompt_version": config.system_prompt_version,
        "temperature": config.temperature,
    }
    canonical = json.dumps(payload, sort_keys=True, ensure_ascii=True)
    return hashlib.sha256(canonical.encode("utf-8")).hexdigest()


def assert_parity(naive_config: ControlledConfig, graph_config: ControlledConfig) -> None:
    """Assert that both mode configs are identical before any provider call.

    Must be called before provider execution. Raises ParityError if the
    fingerprints differ, preventing an unfair comparison from proceeding.

    Args:
        naive_config: Controlled config for the naive mode run.
        graph_config: Controlled config for the graph-guided mode run.

    Raises:
        ParityError: If fingerprints differ, with full diagnostic detail.
    """
    naive_fp = compute_parity_fingerprint(naive_config)
    graph_fp = compute_parity_fingerprint(graph_config)
    if naive_fp != graph_fp:
        raise ParityError(
            "Controlled configuration mismatch detected before provider call.\n"
            f"Naive fingerprint:  {naive_fp}\n"
            f"Graph fingerprint:  {graph_fp}\n"
            f"Naive: {naive_config}\n"
            f"Graph: {graph_config}"
        )
