"""Anthropic Provider — Anthropic API implementation."""

from __future__ import annotations

import os
from typing import Any

from anthropic import Anthropic
from anthropic.types import MessageParam

from ex04.providers.interface import Message, ProviderInterface, ProviderResponse
from ex04.providers.types import ProviderConfig

_DEFAULT_MAX_TOKENS = 4096


class AnthropicProvider(ProviderInterface):
    """Anthropic provider implementation."""

    # noqa: F821
    def __init__(self, config: ProviderConfig) -> None:
        """Initialize the Anthropic provider."""
        api_key_env = config.get("api_key_env", "ANTHROPIC_API_KEY")
        api_key = os.environ.get(api_key_env, "")

        self._client = Anthropic(
            api_key=api_key,
            base_url=config.get("base_url"),
        )
        self._model = str(config.get("model", "claude-sonnet-4-20250514"))
        self._max_tokens = int(config.get("max_tokens", _DEFAULT_MAX_TOKENS))

    def chat(
        self,
        messages: list[Message],
        model: str | None = None,
        base_url: str | None = None,
    ) -> ProviderResponse:
        """Send messages through the Anthropic Messages API."""
        target_model = model or self._model

        system_message = next(
            (message for message in messages if message["role"] == "system"),
            None,
        )

        anthropic_messages: list[MessageParam] = []

        for message in messages:
            role = message["role"]

            if role == "system":
                continue

            anthropic_messages.append(
                {
                    "role": role,
                    "content": message["content"],
                }
            )

        create_kwargs: dict[str, Any] = {
            "model": target_model,
            "messages": anthropic_messages,
            "max_tokens": self._max_tokens,
        }

        if system_message is not None:
            create_kwargs["system"] = system_message["content"]

        response = self._client.messages.create(**create_kwargs)

        text = "".join(
            block.text
            for block in response.content
            if getattr(block, "type", "text") == "text"
            or not isinstance(getattr(block, "type", None), str)
        )

        return ProviderResponse(
            text=text,
            input_tokens=response.usage.input_tokens,
            output_tokens=response.usage.output_tokens,
            model=target_model,
            provider="anthropic",
        )

    def count_tokens(self, text: str) -> int:
        """Count the number of input tokens in text."""
        message: MessageParam = {
            "role": "user",
            "content": text,
        }

        response = self._client.messages.count_tokens(
            model=self._model,
            messages=[message],
        )

        return response.input_tokens
