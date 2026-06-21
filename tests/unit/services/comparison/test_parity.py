"""Tests for controlled-configuration parity fingerprint."""

from __future__ import annotations

import pytest

from ex04.services.comparison.parity import (
    ControlledConfig,
    ParityError,
    assert_parity,
    compute_parity_fingerprint,
)


def _cfg(**overrides: object) -> ControlledConfig:
    defaults: dict[str, object] = dict(
        provider="openai",
        model="gpt-4o",
        temperature=0.0,
        max_tokens=4096,
        system_prompt_version="1.0",
        prompt_envelope_version="1.0",
        output_schema_version="1.0",
        retry_max_attempts=3,
        correctness_gate_version="1.0",
    )
    defaults.update(overrides)
    return ControlledConfig(**defaults)  # type: ignore[arg-type]


def test_fingerprint_is_hex_string() -> None:
    fp = compute_parity_fingerprint(_cfg())
    assert len(fp) == 64
    assert all(c in "0123456789abcdef" for c in fp)


def test_fingerprint_is_stable_across_calls() -> None:
    cfg = _cfg()
    assert compute_parity_fingerprint(cfg) == compute_parity_fingerprint(cfg)


def test_fingerprint_changes_on_model_change() -> None:
    fp1 = compute_parity_fingerprint(_cfg(model="gpt-4o"))
    fp2 = compute_parity_fingerprint(_cfg(model="gpt-4o-mini"))
    assert fp1 != fp2


def test_fingerprint_changes_on_temperature_change() -> None:
    fp1 = compute_parity_fingerprint(_cfg(temperature=0.0))
    fp2 = compute_parity_fingerprint(_cfg(temperature=0.5))
    assert fp1 != fp2


def test_fingerprint_changes_on_provider_change() -> None:
    fp1 = compute_parity_fingerprint(_cfg(provider="openai"))
    fp2 = compute_parity_fingerprint(_cfg(provider="anthropic"))
    assert fp1 != fp2


def test_assert_parity_passes_for_identical_configs() -> None:
    cfg = _cfg()
    assert_parity(cfg, cfg)  # should not raise


def test_assert_parity_raises_on_model_mismatch() -> None:
    naive = _cfg(model="gpt-4o")
    graph = _cfg(model="gpt-4o-mini")
    with pytest.raises(ParityError) as exc_info:
        assert_parity(naive, graph)
    msg = str(exc_info.value)
    assert "fingerprint" in msg.lower()


def test_assert_parity_error_is_actionable() -> None:
    naive = _cfg(provider="openai")
    graph = _cfg(provider="anthropic")
    with pytest.raises(ParityError) as exc_info:
        assert_parity(naive, graph)
    msg = str(exc_info.value)
    # Must show both fingerprints for debugging
    assert "Naive fingerprint" in msg
    assert "Graph fingerprint" in msg


def test_config_is_immutable() -> None:
    cfg = _cfg()
    with pytest.raises(AttributeError):
        cfg.model = "other"  # type: ignore[misc]


def test_fingerprint_ignores_nothing_extra() -> None:
    """Two configs with same controlled fields → same fingerprint."""
    cfg_a = _cfg()
    cfg_b = _cfg()
    assert compute_parity_fingerprint(cfg_a) == compute_parity_fingerprint(cfg_b)
