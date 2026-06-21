"""Rate Limiter — per-provider rate limit tracking and enforcement.

Tracks request timestamps per provider and enforces per-minute and
per-day limits loaded from configuration.

## Contract

| Method | Input | Output |
|---|---|---|
| `load(path)` | str (JSON path) | None |
| `is_within_limit(provider)` | str | bool |
| `get_config(provider)` | str | dict |

Implementation: **Phase 4** (T4.002, extracted from gatekeeper)
"""

from __future__ import annotations

import time
from pathlib import Path
from typing import Any

from ex04.shared.json_utils import load_json


def _default_config() -> dict[str, Any]:
    """Return default rate limit configuration."""
    return {
        "requests_per_minute": 60,
        "requests_per_day": 10000,
        "retry_attempts": 3,
        "retry_delay_seconds": 5,
    }


class RateLimiter:
    """Per-provider rate limit tracker.

    Enforces per-minute and per-day request limits. Timestamps older
    than 24 hours are automatically pruned on each check.

    Attributes:
        _limits: Per-provider rate limit configuration.
        _timestamps: Per-provider request timestamp lists.
    """

    def __init__(self) -> None:
        """Initialize with empty rate limits."""
        self._limits: dict[str, dict[str, Any]] = {}
        self._timestamps: dict[str, list[float]] = {}

    def load(self, path: str) -> None:
        """Load rate limits from a JSON configuration file.

        Args:
            path: Path to the rate limits JSON file.

        Raises:
            FileNotFoundError: If the file does not exist.
            ValueError: If the JSON is malformed.
        """
        config_file = Path(path)
        if not config_file.exists():
            raise FileNotFoundError(f"Rate limits file not found: {path}")

        self._limits = load_json(config_file)

    def get_config(self, provider: str) -> dict[str, Any]:
        """Get rate limit config for a provider, with safe defaults.

        Defaults are overlaid by any provider-specific values, so a partial
        configuration entry (e.g. one missing ``requests_per_minute``) still
        yields a complete config instead of raising a KeyError downstream.

        Args:
            provider: Provider name (e.g. 'openai').

        Returns:
            Dict with the full set of rate limit settings.
        """
        config = _default_config()
        config.update(self._limits.get(provider, {}))
        return config

    def _recent(self, provider: str) -> tuple[int, int]:
        """Prune expired timestamps and count recent requests (no recording).

        Args:
            provider: Provider name to inspect.

        Returns:
            (requests_in_last_minute, requests_in_last_day).
        """
        now = time.time()
        kept = [t for t in self._timestamps.get(provider, []) if t > now - 86400]
        self._timestamps[provider] = kept
        last_minute = sum(1 for t in kept if t > now - 60)
        return last_minute, len(kept)

    def _exceeds(self, provider: str) -> bool:
        """Return True if the provider has hit its per-minute or per-day cap."""
        config = self.get_config(provider)
        last_minute, last_day = self._recent(provider)
        return (
            last_minute >= config["requests_per_minute"]
            or last_day >= config["requests_per_day"]
        )

    def is_within_limit(self, provider: str) -> bool:
        """Check limits and, if within them, record the request timestamp.

        This is the *consuming* check: a True result reserves a slot. For a
        side-effect-free check use :meth:`is_currently_limited`.

        Args:
            provider: Provider name to check.

        Returns:
            True if within limits (and a slot was reserved), else False.
        """
        if self._exceeds(provider):
            return False
        self._timestamps[provider].append(time.time())
        return True

    def is_currently_limited(self, provider: str) -> bool:
        """Report whether a provider is rate limited without recording a request.

        Args:
            provider: Provider name to inspect.

        Returns:
            True if the provider is currently at or over a limit.
        """
        return self._exceeds(provider)

    def is_any_limited(self) -> bool:
        """Check if any configured provider is currently rate limited.

        Uses the non-recording check so that polling status never consumes
        rate-limit budget.

        Returns:
            True if at least one provider is rate limited.
        """
        return any(self.is_currently_limited(provider) for provider in self._limits)
