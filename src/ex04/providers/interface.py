"""Provider Interface — abstract base class for LLM providers.

All LLM calls must flow through this interface to ensure
provider-agnostic design. The Gatekeeper controls rate limits.
Supports custom base_url for proxy/local endpoints.

Implementation: Phase 3 (T3.01–T3.04)
  - T3.01: ProviderInterface (this file)
  - T3.02: OpenAIProvider
  - T3.03: AnthropicProvider
  - T3.04: ProviderFactory
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import TypedDict

from ex04.shared.types_results import ProviderResponse


class Message(TypedDict):
    """A single chat message.

    Attributes:
        role: Message role ('system', 'user', or 'assistant').
        content: Message text content.
    """

    role: str
    content: str


class ProviderInterface(ABC):
    """Abstract interface for LLM providers.

    All LLM calls must flow through this interface to ensure
    provider-agnostic design. The Gatekeeper controls rate limits.
    Supports custom base_url for proxy/local endpoints.
    """

    @abstractmethod
    def chat(
        self,
        messages: list[Message],
        model: str,
        base_url: str | None = None,
    ) -> ProviderResponse:
        """Send a chat completion request to the provider.

        Args:
            messages: List of message dicts with 'role' and 'content' keys.
            model: Model identifier to use.
            base_url: Optional custom API base URL.

        Returns:
            ProviderResponse with text, token counts, and metadata.
        """

    @abstractmethod
    def count_tokens(self, text: str) -> int:
        """Count tokens in text using the provider's tokenizer.

        Args:
            text: Text to count tokens for.

        Returns:
            Number of tokens in the text.
        """
