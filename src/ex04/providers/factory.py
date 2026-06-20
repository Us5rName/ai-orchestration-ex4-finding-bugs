"""Provider Factory — creates provider instances from config.

Implements a registry-based factory for creating provider instances.
Registers OpenAI and Anthropic providers at import time.
Validates that required API key environment variables are set.

Implementation: Phase 3 (T3.04)
"""

from __future__ import annotations

import os
from collections.abc import Callable

from ex04.providers.anthropic_provider import AnthropicProvider
from ex04.providers.interface import ProviderInterface
from ex04.providers.openai_provider import OpenAIProvider
from ex04.providers.types import ProviderConfig

ProviderConstructor = Callable[[ProviderConfig], ProviderInterface]


class ProviderFactory:
    """Factory for creating provider instances from configuration.

    Uses a registry pattern to map provider names to provider constructors.
    Validates required API key environment variables before instantiation.

    Attributes:
        _registry: Mapping of provider names to provider constructors.
    """

    _registry: dict[str, ProviderConstructor] = {}

    @classmethod
    def register(
        cls,
        name: str,
        provider_constructor: ProviderConstructor,
    ) -> None:
        """Register a provider constructor under a name.

        Args:
            name: Provider name to register under.
            provider_constructor: Callable that creates a provider from config.
        """
        cls._registry[name] = provider_constructor

    @classmethod
    def create(
        cls,
        provider_name: str,
        config: ProviderConfig,
    ) -> ProviderInterface:
        """Create a provider instance from configuration.

        Args:
            provider_name: Provider name, such as ``openai`` or ``anthropic``.
            config: Provider configuration.

        Returns:
            Configured provider instance.

        Raises:
            ValueError: If the provider name is not registered.
            RuntimeError: If the required API key is unavailable.
        """
        provider_constructor = cls._registry.get(provider_name)

        if provider_constructor is None:
            raise ValueError(f"Unknown provider: {provider_name=!r}")

        api_key_env = config.get("api_key_env")

        if api_key_env and not os.environ.get(api_key_env):
            raise RuntimeError(f"Required API key environment variable not set: {api_key_env}")

        return provider_constructor(config)


ProviderFactory.register("openai", OpenAIProvider)
ProviderFactory.register("anthropic", AnthropicProvider)
