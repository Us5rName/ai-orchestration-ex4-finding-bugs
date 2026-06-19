"""API Gatekeeper — centralized API call routing with rate limiting.

Implements GatekeeperInterface with rate limiting, FIFO queuing, retry
logic, and call logging. All LLM calls flow through this gatekeeper.

Rate limits are delegated to RateLimiter. Provider instances are created
via ProviderFactory (lazy import to avoid circular dependency).

## Contract (GatekeeperInterface)

| Method | Input | Output | Phase |
|---|---|---|---|
| `send(provider, messages)` | str, list[dict] | ProviderResponse | P4 |
| `get_call_log()` | — | list[dict] | P4 |
| `get_queue_status()` | — | dict | P4 |

Implementation: **Phase 4** (T4.002)
"""

from __future__ import annotations

import time
from abc import ABC, abstractmethod
from collections import deque
from datetime import datetime
from typing import Any

from ex04.shared.rate_limiter import RateLimiter
from ex04.shared.types_results import ProviderResponse


class GatekeeperInterface(ABC):
    """Abstract API gatekeeper interface."""

    @abstractmethod
    def send(self, provider: str, messages: list[dict[str, str]]) -> ProviderResponse:
        """Execute an API call through the gatekeeper."""

    @abstractmethod
    def get_call_log(self) -> list[dict[str, Any]]:
        """Retrieve the full call log."""

    @abstractmethod
    def get_queue_status(self) -> dict[str, Any]:
        """Retrieve the current queue status."""


class ApiGatekeeper(GatekeeperInterface):
    """Centralized API call manager with rate limiting and queuing.

    Delegates rate limiting to RateLimiter and provider creation to
    ProviderFactory. Queues overflow requests and logs all calls.
    """

    def __init__(
        self,
        rate_limits_path: str = "",
        default_model: str = "gpt-4o-mini",
    ) -> None:
        """Initialize gatekeeper with optional rate limits config.

        Args:
            rate_limits_path: Path to rate_limits.json. Empty disables.
            default_model: Default LLM model to use for API calls.
        """
        self._limiter = RateLimiter()
        self._call_log: list[dict[str, Any]] = []
        self._queue: deque[dict[str, Any]] = deque()
        self._default_model = default_model
        if rate_limits_path:
            self._limiter.load(rate_limits_path)

    def send(self, provider: str, messages: list[dict[str, str]]) -> ProviderResponse:
        """Execute an API call through the gatekeeper.

        Args:
            provider: Provider name (e.g. 'openai', 'anthropic').
            messages: List of message dicts with 'role' and 'content'.

        Returns:
            ProviderResponse with text, token counts, and metadata.

        Raises:
            RuntimeError: If all retry attempts fail.
            ValueError: If the provider is not registered.
        """
        # Lazy import to avoid circular dependency
        from ex04.providers.factory import ProviderFactory

        config = self._limiter.get_config(provider)
        max_retries = config.get("retry_attempts", 3)
        retry_delay = config.get("retry_delay_seconds", 5)

        for attempt in range(max_retries):
            try:
                if not self._limiter.is_within_limit(provider):
                    self._queue.append({"provider": provider, "messages": messages})
                    time.sleep(retry_delay)
                    continue

                provider_instance = ProviderFactory.create(
                    provider,
                    {
                        "api_key_env": f"{provider.upper()}_API_KEY",
                        "model": self._default_model,
                        "base_url": None,
                    },
                )
                response = provider_instance.chat(messages=messages, model=self._default_model)

                self._call_log.append(
                    {
                        "timestamp": datetime.now(),
                        "provider": provider,
                        "status": "success",
                        "input_tokens": response.input_tokens,
                        "output_tokens": response.output_tokens,
                        "attempt": attempt + 1,
                    }
                )
                return response

            except Exception as exc:
                if attempt == max_retries - 1:
                    self._call_log.append(
                        {
                            "timestamp": datetime.now(),
                            "provider": provider,
                            "status": "failed",
                            "error": str(exc),
                            "attempt": attempt + 1,
                        }
                    )
                    raise
                time.sleep(retry_delay)

    def get_call_log(self) -> list[dict[str, Any]]:
        """Retrieve the full call log."""
        return list(self._call_log)

    def get_queue_status(self) -> dict[str, Any]:
        """Retrieve the current queue status."""
        return {
            "queue_size": len(self._queue),
            "is_processing": len(self._queue) > 0,
            "rate_limited": self._limiter.is_any_limited(),
        }
