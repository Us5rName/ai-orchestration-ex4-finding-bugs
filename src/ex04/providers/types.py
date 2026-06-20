"""Shared provider type definitions."""

from __future__ import annotations

from typing import TypedDict


class ProviderConfig(TypedDict, total=False):
    """Configuration shared by provider implementations."""

    api_key_env: str
    model: str
    base_url: str | None
    max_tokens: int
