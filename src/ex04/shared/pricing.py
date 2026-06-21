"""Pricing loader and cost estimator for LLM provider models.

Reads config/pricing.json at runtime. Prices are estimates only —
actual billed costs depend on provider billing details.

Traceability: [TODO P7-R02], [Correction #8]
"""

from __future__ import annotations

from pathlib import Path

from ex04.shared.json_utils import load_json

_DEFAULT_PRICING_PATH = Path(__file__).parent.parent.parent.parent / "config" / "pricing.json"


def load_pricing(path: Path | None = None) -> dict[str, object]:
    """Load pricing configuration from JSON file."""
    resolved = path or _DEFAULT_PRICING_PATH
    return load_json(resolved)


def lookup_model_pricing(
    provider: str, model: str, config: dict[str, object] | None = None
) -> dict[str, float] | None:
    """Return {'input_price': float, 'output_price': float} for a model, or None."""
    if config is None:
        config = load_pricing()
    for entry in config.get("models", []):  # type: ignore[union-attr]
        if entry.get("provider") == provider and entry.get("model") == model:
            return {
                "input_price": float(entry["input_price"]),  # type: ignore[arg-type]
                "output_price": float(entry["output_price"]),  # type: ignore[arg-type]
            }
    return None


def estimate_cost(
    provider: str,
    model: str,
    input_tokens: int | None,
    output_tokens: int | None,
    config: dict[str, object] | None = None,
) -> float | None:
    """Estimate cost in USD for a given token count.

    Returns None when tokens are unavailable or model pricing is unknown.
    Result is an estimate — not actual billed cost.

    Formula: (input_tokens / 1_000_000) * input_price
           + (output_tokens / 1_000_000) * output_price
    """
    if input_tokens is None or output_tokens is None:
        return None
    prices = lookup_model_pricing(provider, model, config)
    if prices is None:
        return None
    return (
        (input_tokens / 1_000_000) * prices["input_price"]
        + (output_tokens / 1_000_000) * prices["output_price"]
    )
