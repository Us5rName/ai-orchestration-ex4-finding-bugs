"""Anthropic Provider — Anthropic API implementation.

Implements ProviderInterface using the Anthropic Python SDK.
Uses the Anthropic API for token counting.

Implementation: Phase 3 (T3.03)
"""

from __future__ import annotations

import os
from typing import Any

from anthropic import Anthropic

from ex04.providers.interface import Message, ProviderInterface, ProviderResponse


class AnthropicProvider(ProviderInterface):
    """Anthropic provider implementation.

    Attributes:
        _client: Anthropic API client instance.
        _model: Default model identifier.
    """

    def __init__(self, config: dict[str, Any]) -> None:
        """Initialize Anthropic provider.

        Args:
            config: Config dict with 'api_key_env', 'model', 'base_url'.
        """
        api_key = os.environ.get(config.get("api_key_env", "ANTHROPIC_API_KEY"), "")
        self._client = Anthropic(
            api_key=api_key,
            base_url=config.get("base_url"),  # type: ignore[arg-type]
        )
        self._model = config.get("model", "claude-sonnet-4-20250514")

    def chat(
        self,
        messages: list[Message],
        model: str | None = None,
        base_url: str | None = None,
    ) -> ProviderResponse:
        """Send a message to Anthropic.

        Extracts system messages and user messages, then sends them
        via the Anthropic Messages API.

        Args:
            messages: List of message dicts with 'role' and 'content' keys.
            model: Model identifier to use (overrides config default).
            base_url: Optional custom API base URL.

        Returns:
            ProviderResponse with text, token counts, and metadata.
        """
        target_model = model or self._model
        system_msg = next((msg for msg in messages if msg.get("role") == "system"), None)
        user_msgs = [
            {"role": msg["role"], "content": msg["content"]}
            for msg in messages
            if msg.get("role") != "system"
        ]
        response = self._client.messages.create(
            model=target_model,
            messages=user_msgs,
            system=system_msg["content"] if system_msg else None,  # type: ignore[arg-type]
        )
        text = response.content[0].text if response.content else ""
        usage = response.usage
        return ProviderResponse(
            text=text,
            input_tokens=usage.input_tokens if usage else 0,
            output_tokens=usage.output_tokens if usage else 0,
            model=target_model,
            provider="anthropic",
        )

    def count_tokens(self, text: str) -> int:
        """Count tokens in text using Anthropic tokenizer.

        Args:
            text: Text to count tokens for.

        Returns:
            Number of tokens in the text.
        """
        return self._client.count_tokens(text=text)
