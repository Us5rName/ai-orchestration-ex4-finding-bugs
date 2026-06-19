"""API Gatekeeper interface — contract for centralized API call management.

This module defines the abstract interface that all API gatekeepers must
implement. The actual implementation will be provided in **Phase 4** when
the agent nodes require LLM call routing.

## Contract

| Method | Input | Output | Phase |
|---|---|---|---|
| `send(provider, messages)` | str, list[Message] | ProviderResponse | P4 |
| `get_call_log()` | — | list[dict] | P4 |
| `get_queue_status()` | — | dict | P4 |

## Features (to be implemented in Phase 4)

- Rate limiting from `config/rate_limits.json`
- FIFO queue for overflow requests
- Retry logic with configurable attempts/delay
- Call logging with timestamps

## Usage

```python
from ex04.shared.gatekeeper import GatekeeperInterface

class MyGatekeeper(GatekeeperInterface):
    def send(self, provider: str, messages: list[dict]) -> ProviderResponse: ...
    def get_call_log(self) -> list[dict]: ...
    def get_queue_status(self) -> dict: ...
```

Actual implementation: **Phase 4** (agent nodes call gatekeeper for LLM calls).
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any

from ex04.shared.types_results import ProviderResponse


class GatekeeperInterface(ABC):
    """Abstract API gatekeeper interface.

    All API gatekeepers must implement these methods to ensure consistent
    API call routing, rate limiting, and monitoring across the system.

    Attributes:
        _call_log: Internal log of all API calls with timestamps.
    """

    @abstractmethod
    def send(self, provider: str, messages: list[dict[str, str]]) -> ProviderResponse:
        """Execute an API call through the gatekeeper.

        Enforces rate limits, queues overflow requests, and retries on failure.

        Args:
            provider: Provider name (e.g. 'openai', 'anthropic').
            messages: List of message dicts with 'role' and 'content' keys.

        Returns:
            ProviderResponse with text, token counts, and metadata.

        Raises:
            RuntimeError: If all retry attempts fail.
        """

    @abstractmethod
    def get_call_log(self) -> list[dict[str, Any]]:
        """Retrieve the full call log.

        Returns:
            List of call records, each containing timestamp, provider,
            status, and token information.
        """

    @abstractmethod
    def get_queue_status(self) -> dict[str, Any]:
        """Retrieve the current queue status.

        Returns:
            Dictionary with 'queue_size', 'is_processing', and 'rate_limited' keys.
        """
