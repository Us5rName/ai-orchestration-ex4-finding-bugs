"""Token Tracker interface — contract for API token usage tracking.

This module defines the abstract interface that all token trackers must
implement. The actual implementation will be provided in **Phase 6** when
the comparison service needs to track and compare token usage.

## Contract

| Method | Input | Output | Phase |
|---|---|---|---|
| `record(metrics)` | TokenMetrics | None | P6 |
| `total(provider)` | str | int | P6 |
| `by_session(session_id)` | str | dict | P6 |
| `export()` | — | dict | P6 |

## Features (to be implemented in Phase 6)

- Thread-safe recording of token usage per session
- Cumulative token totals by provider
- Session-level metrics aggregation
- Serializable export for reporting

## Usage

```python
from ex04.shared.token_tracker import TokenTrackerInterface

class MyTokenTracker(TokenTrackerInterface):
    def record(self, metrics: TokenMetrics) -> None: ...
    def total(self, provider: str) -> int: ...
    def by_session(self, session_id: str) -> dict: ...
    def export(self) -> dict: ...
```

Actual implementation: **Phase 6** (comparison needs token tracking).
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any

from ex04.shared.types_metrics import TokenMetrics


class TokenTrackerInterface(ABC):
    """Abstract token tracker interface.

    All token trackers must implement these methods to ensure consistent
    token usage tracking across the system, enabling comparison between
    naive and graph-guided approaches.

    Attributes:
        _sessions: Internal dict mapping session IDs to their token records.
    """

    @abstractmethod
    def record(self, metrics: TokenMetrics) -> None:
        """Record token usage for a single API call.

        Args:
            metrics: TokenMetrics instance with input/output counts and metadata.
        """

    @abstractmethod
    def total(self, provider: str) -> int:
        """Get cumulative token count for a provider.

        Args:
            provider: Provider name (e.g. 'openai', 'anthropic').

        Returns:
            Total tokens used across all sessions for this provider.
        """

    @abstractmethod
    def by_session(self, session_id: str) -> dict[str, Any]:
        """Get all token metrics for a specific session.

        Args:
            session_id: Unique session identifier.

        Returns:
            Dictionary with 'total_tokens', 'calls', and 'providers' keys.
        """

    @abstractmethod
    def export(self) -> dict[str, Any]:
        """Export all tracked token data as a serializable dictionary.

        Returns:
            Dictionary suitable for JSON serialization, containing
            per-provider totals and per-session breakdowns.
        """
