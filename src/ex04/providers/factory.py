"""Provider Factory — creates provider instances from config.

Implements a registry-based factory for creating provider instances.
Registers OpenAI and Anthropic providers at import time.
Validates that required API key environment variables are set.

Implementation: Phase 3 (T3.04)
"""

from __future__ import annotations

import os
from typing import Any

from ex04.providers.anthropic_provider import AnthropicProvider
from ex04.providers.interface import ProviderInterface
from ex04.providers.openai_provider import OpenAIProvider


class ProviderFactory:
    """Factory for creating provider instances from configuration.

    Uses a registry pattern to map provider names to provider classes.
    Validates that required API key environment variables are set before
    instantiation.

    Attributes:
        _registry: Mapping of provider names to provider classes.
    """

    _registry: dict[str, type[ProviderInterface]] = {}

    @classmethod
    def register(cls, name: str, provider_class: type[ProviderInterface]) -> None:
        """Register a provider class under a name.

        Args:
            name: Provider name to register under.
            provider_class: Provider class to register.
        """
        cls._registry[name] = provider_class

    @classmethod
    def create(cls, provider_name: str, config: dict[str, Any]) -> ProviderInterface:
        """Create a provider instance from configuration.

        Validates that the provider is registered and that the required
        API key environment variable is set before instantiation.

        Args:
            provider_name: Provider name (e.g. 'openai', 'anthropic').
            config: Config dict with 'api_key_env', 'model', 'base_url'.

        Returns:
            ProviderInterface instance configured with the given settings.

        Raises:
            ValueError: If the provider name is not registered.
            RuntimeError: If the required API key environment variable is missing.
        """
        if provider_name not in cls._registry:
            raise ValueError(f"Unknown provider: {provider_name}")
        api_key_env = config.get("api_key_env")
        if api_key_env and not os.environ.get(api_key_env):
            raise RuntimeError(f"Required API key environment variable not set: {api_key_env}")
        return cls._registry[provider_name](config)


# Register available providers at import time
ProviderFactory.register("openai", OpenAIProvider)
ProviderFactory.register("anthropic", AnthropicProvider)
