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

# Anthropic's Messages API requires an explicit output cap. This is the
# engineering fallback used only when the caller does not supply ``max_tokens``
# via config (config/setup.json is the preferred source — PRD NFR-4).
_DEFAULT_MAX_TOKENS = 4096


class AnthropicProvider(ProviderInterface):
    """Anthropic provider implementation.

    Attributes:
        _client: Anthropic API client instance.
        _model: Default model identifier.
        _max_tokens: Output token cap sent with every request.
    """

    def __init__(self, config: dict[str, Any]) -> None:
        """Initialize Anthropic provider.

        Args:
            config: Config dict with 'api_key_env', 'model', 'base_url',
                and optional 'max_tokens' (output cap).
        """
        api_key = os.environ.get(config.get("api_key_env", "ANTHROPIC_API_KEY"), "")
        self._client = Anthropic(
            api_key=api_key,
            base_url=config.get("base_url"),  # type: ignore[arg-type]
        )
        self._model = config.get("model", "claude-sonnet-4-20250514")
        self._max_tokens = int(config.get("max_tokens", _DEFAULT_MAX_TOKENS))

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
        # ``max_tokens`` is required by the Messages API; ``system`` is omitted
        # entirely (not passed as None) when there is no system message.
        create_kwargs: dict[str, Any] = {
            "model": target_model,
            "messages": user_msgs,
            "max_tokens": self._max_tokens,
        }
        if system_msg:
            create_kwargs["system"] = system_msg["content"]
        response = self._client.messages.create(**create_kwargs)
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
        """Count tokens in text using the Anthropic token-counting endpoint.

        The legacy ``client.count_tokens`` helper was removed from the SDK;
        token counting for Claude 3+ models is server-side via
        ``messages.count_tokens``.

        Args:
            text: Text to count tokens for.

        Returns:
            Number of input tokens the text would consume.
        """
        response = self._client.messages.count_tokens(
            model=self._model,
            messages=[{"role": "user", "content": text}],
        )
        return response.input_tokens
