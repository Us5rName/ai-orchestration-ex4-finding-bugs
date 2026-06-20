"""Tests for pricing loader and cost estimator.

Traceability: [TODO P7-R02], [Correction #8]
"""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from ex04.shared.pricing import estimate_cost, load_pricing, lookup_model_pricing


@pytest.fixture
def mock_config(tmp_path: Path) -> dict[str, object]:
    cfg = {
        "version": "1.0",
        "units": "per_million_tokens",
        "models": [
            {
                "provider": "anthropic",
                "model": "claude-haiku-4-5-20251001",
                "input_price": 0.80,
                "output_price": 4.00,
            },
            {
                "provider": "openai",
                "model": "gpt-4o-mini",
                "input_price": 0.15,
                "output_price": 0.60,
            },
        ],
    }
    return cfg


def test_load_pricing_reads_default_file() -> None:
    """Default pricing.json file loads without error."""
    config = load_pricing()
    assert "models" in config
    assert config.get("units") == "per_million_tokens"


def test_lookup_known_model(mock_config: dict[str, object]) -> None:
    prices = lookup_model_pricing("anthropic", "claude-haiku-4-5-20251001", mock_config)
    assert prices is not None
    assert prices["input_price"] == 0.80
    assert prices["output_price"] == 4.00


def test_lookup_unknown_model_returns_none(mock_config: dict[str, object]) -> None:
    result = lookup_model_pricing("anthropic", "claude-3-haiku-20240307", mock_config)
    assert result is None


def test_lookup_wrong_provider_returns_none(mock_config: dict[str, object]) -> None:
    result = lookup_model_pricing("openai", "claude-haiku-4-5-20251001", mock_config)
    assert result is None


def test_estimate_cost_per_million_units(mock_config: dict[str, object]) -> None:
    """1M input + 1M output for haiku = 0.80 + 4.00 = 4.80."""
    cost = estimate_cost("anthropic", "claude-haiku-4-5-20251001", 1_000_000, 1_000_000, mock_config)
    assert cost is not None
    assert abs(cost - 4.80) < 1e-9


def test_estimate_cost_returns_none_when_tokens_none(mock_config: dict[str, object]) -> None:
    cost = estimate_cost("anthropic", "claude-haiku-4-5-20251001", None, None, mock_config)
    assert cost is None


def test_estimate_cost_returns_none_for_unknown_model(mock_config: dict[str, object]) -> None:
    cost = estimate_cost("anthropic", "claude-3-haiku-20240307", 100, 50, mock_config)
    assert cost is None


def test_no_retired_models_in_active_list() -> None:
    """Retired models must not appear in the active models list."""
    config = load_pricing()
    retired = set(config.get("retired_models", []))  # type: ignore[arg-type]
    active_models = {
        entry["model"]
        for entry in config.get("models", [])  # type: ignore[union-attr]
    }
    overlap = retired & active_models
    assert not overlap, f"Retired models in active list: {overlap}"


def test_pricing_config_has_required_fields() -> None:
    config = load_pricing()
    assert "version" in config
    assert "retrieval_date" in config
    assert "effective_date" in config
    assert "units" in config
    assert "note" in config
    assert config["units"] == "per_million_tokens"
