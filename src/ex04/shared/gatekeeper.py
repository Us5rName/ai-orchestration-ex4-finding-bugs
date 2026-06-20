"""API Gatekeeper — centralized API call routing with rate limiting.

Implements GatekeeperInterface. All LLM calls flow through this gatekeeper,
which owns the FIFO request queue and delegates the per-call mechanics (slot
waiting, retry, logging) to CallExecutor, rate limiting to RateLimiter, and
provider construction/caching to ProviderPool.

A rate-limited request waits in the FIFO queue for a free slot rather than
being silently dropped; ``send`` always returns a ProviderResponse or raises.

## Contract (GatekeeperInterface)

| Method | Input | Output | Phase |
|---|---|---|---|
| `send(provider, messages)` | str, list[dict] | ProviderResponse | P4 |
| `get_call_log()` | — | list[dict] | P4 |
| `get_queue_status()` | — | dict | P4 |

Implementation: **Phase 4** (T4.002)
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from collections import deque
from typing import Any

from ex04.shared.call_executor import CallExecutor
from ex04.shared.provider_pool import ProviderPool
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

    Owns the FIFO request queue and delegates rate limiting, provider
    creation/caching, and per-call dispatch to focused collaborators.
    """

    def __init__(
        self,
        rate_limits_path: str = "",
        provider_configs: dict[str, dict[str, Any]] | None = None,
    ) -> None:
        """Initialize gatekeeper with optional rate limits and provider config.

        Args:
            rate_limits_path: Path to rate_limits.json. Empty disables loading.
            provider_configs: Per-provider config (model, base_url, max_tokens,
                api_key_env) used to build providers.
        """
        self._limiter = RateLimiter()
        self._pool = ProviderPool(provider_configs)
        self._queue: deque[dict[str, Any]] = deque()
        if rate_limits_path:
            self._limiter.load(rate_limits_path)
        self._executor = CallExecutor(self._limiter, self._pool)

    def send(self, provider: str, messages: list[dict[str, str]]) -> ProviderResponse:
        """Execute an API call through the gatekeeper.

        The request is enqueued (FIFO) for the duration of the call and removed
        when it completes or fails. Returns a ProviderResponse or raises — it
        never returns None.

        Args:
            provider: Provider name (e.g. 'openai', 'anthropic').
            messages: List of message dicts with 'role' and 'content'.

        Returns:
            ProviderResponse with text, token counts, and metadata.

        Raises:
            RuntimeError: If a slot never frees, or all retries fail.
            ValueError: If the provider is not registered.
        """
        self._queue.append({"provider": provider, "messages": messages})
        try:
            return self._executor.run(provider, messages)
        finally:
            self._queue.popleft()

    def get_call_log(self) -> list[dict[str, Any]]:
        """Retrieve the full call log."""
        return self._executor.get_log()

    def get_queue_status(self) -> dict[str, Any]:
        """Retrieve the current queue status."""
        return {
            "queue_size": len(self._queue),
            "is_processing": len(self._queue) > 0,
            "rate_limited": self._limiter.is_any_limited(),
        }
