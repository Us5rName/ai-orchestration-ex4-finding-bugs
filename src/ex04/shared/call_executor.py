"""Call Executor — rate-limit-aware provider dispatch with retry and logging.

Encapsulates the per-call mechanics used by the gatekeeper: wait (FIFO) for a
free rate-limit slot, dispatch the provider call with retry on transient
errors, and log every outcome. A call always yields a ProviderResponse or
raises — it never returns None.

Implementation: Phase 4 (T4.002, extracted from gatekeeper)
"""

from __future__ import annotations

import time
from datetime import datetime
from typing import Any

from ex04.providers.interface import Message
from ex04.shared.provider_pool import ProviderPool
from ex04.shared.rate_limiter import RateLimiter
from ex04.shared.types_results import ProviderResponse


class CallExecutor:
    """Await a rate-limit slot, dispatch a provider call, and log it.

    Attributes:
        _limiter: Rate limiter providing slot reservation and config.
        _pool: Provider pool building/caching provider instances.
        _log: Structured log of every attempted call.
    """

    def __init__(self, limiter: RateLimiter, pool: ProviderPool) -> None:
        """Store the rate limiter and provider pool; start an empty log."""
        self._limiter = limiter
        self._pool = pool
        self._log: list[dict[str, Any]] = []

    def get_log(self) -> list[dict[str, Any]]:
        """Return a copy of the call log."""
        return list(self._log)

    def run(self, provider: str, messages: list[Message]) -> ProviderResponse:
        """Wait for a slot, then dispatch with retry.

        Args:
            provider: Provider name (e.g. 'openai', 'anthropic').
            messages: Chat messages to send.

        Returns:
            The provider's ProviderResponse.

        Raises:
            RuntimeError: If a slot never frees, or all retries are exhausted.
        """
        config = self._limiter.get_config(provider)
        max_attempts = config.get("retry_attempts", 3)
        retry_delay = config.get("retry_delay_seconds", 5)
        self._await_slot(provider, max_attempts, retry_delay)
        return self._dispatch(provider, messages, max_attempts, retry_delay)

    def _await_slot(self, provider: str, max_waits: int, retry_delay: int) -> None:
        """Block until the provider has a free rate-limit slot (FIFO wait).

        Raises:
            RuntimeError: If no slot frees within ``max_waits`` waits.
        """
        for _ in range(max(max_waits, 1)):
            if self._limiter.is_within_limit(provider):
                return
            time.sleep(retry_delay)
        raise RuntimeError(f"Rate limit exceeded for '{provider}'; no slot available")

    def _dispatch(
        self, provider: str, messages: list[Message], max_attempts: int, retry_delay: int
    ) -> ProviderResponse:
        """Send the request to the provider, retrying transient failures.

        Raises:
            Exception: Re-raises the provider error after the final attempt.
        """
        for attempt in range(max(max_attempts, 1)):
            try:
                instance = self._pool.get(provider)
                response = instance.chat(messages=messages, model=self._pool.model_for(provider))
                self._record(provider, "success", attempt + 1, response=response)
                return response
            except Exception as exc:
                if attempt == max_attempts - 1:
                    self._record(provider, "failed", attempt + 1, error=str(exc))
                    raise
                time.sleep(retry_delay)
        raise RuntimeError(f"All {max_attempts} attempts failed for '{provider}'")

    def _record(
        self,
        provider: str,
        status: str,
        attempt: int,
        response: ProviderResponse | None = None,
        error: str | None = None,
    ) -> None:
        """Append a structured entry to the call log."""
        entry: dict[str, Any] = {
            "timestamp": datetime.now(),
            "provider": provider,
            "status": status,
            "attempt": attempt,
        }
        if response is not None:
            entry["input_tokens"] = response.input_tokens
            entry["output_tokens"] = response.output_tokens
        if error is not None:
            entry["error"] = error
        self._log.append(entry)
