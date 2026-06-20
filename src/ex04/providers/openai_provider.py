"""OpenAI Provider — OpenAI API implementation.

Implements ProviderInterface using the OpenAI Python SDK.
Uses tiktoken for token counting.

Implementation: Phase 3 (T3.02)
"""

from __future__ import annotations

import os

import tiktoken
from openai import OpenAI

from ex04.providers.interface import Message, ProviderInterface, ProviderResponse
from ex04.providers.types import ProviderConfig

# Current default tokenizer for the GPT-4o family; used when a model name
# (e.g. a custom/proxy/local endpoint model) is not in tiktoken's registry.
_FALLBACK_ENCODING = "o200k_base"


class OpenAIProvider(ProviderInterface):
    """OpenAI provider implementation.

    Attributes:
        _client: OpenAI API client instance.
        _model: Default model identifier.
        _encoding: Tiktoken encoding for the default model.
    """

    def __init__(self, config: ProviderConfig) -> None:
        """Initialize OpenAI provider.

        Args:
            config: Config dict with 'api_key_env', 'model', 'base_url'.
        """
        api_key = os.environ.get(config.get("api_key_env", "OPENAI_API_KEY"), "")
        self._client = OpenAI(
            api_key=api_key,
            base_url=config.get("base_url"),  # type: ignore[arg-type]
        )
        self._model = config.get("model", "gpt-4o-mini")
        try:
            self._encoding = tiktoken.encoding_for_model(self._model)
        except KeyError:
            # Custom/proxy/local model names have no tiktoken mapping; fall
            # back to the default tokenizer instead of crashing construction.
            self._encoding = tiktoken.get_encoding(_FALLBACK_ENCODING)

    def chat(
        self,
        messages: list[Message],
        model: str | None = None,
        base_url: str | None = None,
    ) -> ProviderResponse:
        """Send a chat completion request to OpenAI.

        Args:
            messages: List of message dicts with 'role' and 'content' keys.
            model: Model identifier to use (overrides config default).
            base_url: Optional custom API base URL.

        Returns:
            ProviderResponse with text, token counts, and metadata.
        """
        target_model = model or self._model
        response = self._client.chat.completions.create(
            model=target_model,
            messages=messages,  # type: ignore[arg-type]
        )
        choice = response.choices[0] if response.choices else None
        usage = response.usage
        return ProviderResponse(
            text=choice.message.content if choice and choice.message.content else "",
            input_tokens=usage.prompt_tokens if usage else 0,
            output_tokens=usage.completion_tokens if usage else 0,
            model=target_model,
            provider="openai",
        )

    def count_tokens(self, text: str) -> int:
        """Count tokens in text using tiktoken.

        Args:
            text: Text to count tokens for.

        Returns:
            Number of tokens in the text.
        """
        return len(self._encoding.encode(text))
