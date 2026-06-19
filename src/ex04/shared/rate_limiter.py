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

import json
import time
from pathlib import Path
from typing import Any


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

        try:
            raw = config_file.read_text(encoding="utf-8")
            self._limits = json.loads(raw)
        except json.JSONDecodeError as exc:
            raise ValueError(f"Malformed JSON in {path}: {exc}") from exc

    def get_config(self, provider: str) -> dict[str, Any]:
        """Get rate limit config for a provider, with safe defaults.

        Args:
            provider: Provider name (e.g. 'openai').

        Returns:
            Dict with rate limit settings.
        """
        return self._limits.get(provider, _default_config())

    def is_within_limit(self, provider: str) -> bool:
        """Check if the provider is within rate limits.

        Prunes timestamps older than 24 hours, then checks per-minute
        and per-day limits. Records the current request timestamp if
        within limits.

        Args:
            provider: Provider name to check.

        Returns:
            True if within limits, False if rate limited.
        """
        config = self.get_config(provider)
        now = time.time()
        day_ago = now - 86400
        minute_ago = now - 60

        if provider not in self._timestamps:
            self._timestamps[provider] = []

        # Prune old entries
        self._timestamps[provider] = [t for t in self._timestamps[provider] if t > day_ago]

        requests_last_minute = sum(1 for t in self._timestamps[provider] if t > minute_ago)
        requests_last_day = len(self._timestamps[provider])

        if requests_last_minute >= config["requests_per_minute"]:
            return False
        if requests_last_day >= config["requests_per_day"]:
            return False

        self._timestamps[provider].append(now)
        return True

    def is_any_limited(self) -> bool:
        """Check if any configured provider is currently rate limited.

        Returns:
            True if at least one provider is rate limited.
        """
        return any(not self.is_within_limit(provider) for provider in self._limits)
