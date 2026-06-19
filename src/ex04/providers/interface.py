"""Provider Interface — abstract base class for LLM providers.

All LLM calls must flow through this interface to ensure
provider-agnostic design. The Gatekeeper controls rate limits.
Supports custom base_url for proxy/local endpoints.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any


class ProviderInterface(ABC):
    """Abstract interface for LLM providers.

    All LLM calls must flow through this interface to ensure
    provider-agnostic design. The Gatekeeper controls rate limits.
    Supports custom base_url for proxy/local endpoints.
    """

    @abstractmethod
    def chat(
        self,
        messages: list[dict[str, str]],
        model: str,
        base_url: str | None = None,
    ) -> Any:
        """Send a chat completion request to the provider.

        Args:
            messages: List of message dicts with 'role' and 'content' keys.
            model: Model identifier to use.
            base_url: Optional custom API base URL.

        Returns:
            ProviderResponse with content, tokens, and metadata.
        """

    @abstractmethod
    def count_tokens(self, text: str) -> int:
        """Count tokens in text using the provider's tokenizer.

        Args:
            text: Text to count tokens for.

        Returns:
            Number of tokens in the text.
        """


class ProviderFactory:
    """Create provider instance from configuration.

    Attributes:
        _registry: Mapping of provider names to provider classes.
    """

    _registry: dict[str, type[ProviderInterface]] = {}

    @staticmethod
    def create(provider_name: str, config: dict[str, Any]) -> ProviderInterface:
        """Create a provider instance from configuration.

        Args:
            provider_name: Provider name (e.g. 'openai', 'anthropic').
            config: Config dict with 'name', 'model', 'api_key_env', 'base_url'.

        Returns:
            ProviderInterface instance configured with the given settings.

        Raises:
            ValueError: If the provider name is not registered.
        """
        if provider_name not in ProviderFactory._registry:
            raise ValueError(f"Unknown provider: {provider_name}")
        return ProviderFactory._registry[provider_name](config)

    @staticmethod
    def register(name: str, provider_class: type[ProviderInterface]) -> None:
        """Register a provider class under a name.

        Args:
            name: Provider name to register under.
            provider_class: Provider class to register.
        """
        ProviderFactory._registry[name] = provider_class
