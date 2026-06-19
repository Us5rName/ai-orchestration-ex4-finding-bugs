"""Tests for the OpenAI Provider — T3.02.

Uses mocked OpenAI client — no real API calls.
"""

from __future__ import annotations

from unittest.mock import MagicMock, patch

from ex04.providers.interface import ProviderResponse
from ex04.providers.openai_provider import OpenAIProvider


class TestOpenAIProvider:
    """Tests for OpenAIProvider."""

    def _make_mock_response(self):
        """Create a mock OpenAI API response."""
        choice = MagicMock()
        choice.message.content = "Mocked response"
        usage = MagicMock(prompt_tokens=10, completion_tokens=5)
        mock_resp = MagicMock(choices=[choice], usage=usage)
        return mock_resp

    @patch("ex04.providers.openai_provider.OpenAI")
    @patch("ex04.providers.openai_provider.tiktoken")
    def test_chat_returns_provider_response(self, mock_tiktoken, mock_openai):
        """chat() returns a ProviderResponse with correct fields."""
        mock_client = MagicMock()
        mock_openai.return_value = mock_client
        mock_client.chat.completions.create.return_value = self._make_mock_response()
        mock_tiktoken.encoding_for_model.return_value = MagicMock(encode=lambda x: [1, 2, 3])

        provider = OpenAIProvider({"api_key_env": "OPENAI_API_KEY", "model": "gpt-4o-mini"})
        response = provider.chat([{"role": "user", "content": "hello"}])

        assert isinstance(response, ProviderResponse)
        assert response.text == "Mocked response"
        assert response.input_tokens == 10
        assert response.output_tokens == 5
        assert response.model == "gpt-4o-mini"
        assert response.provider == "openai"

    @patch("ex04.providers.openai_provider.OpenAI")
    @patch("ex04.providers.openai_provider.tiktoken")
    def test_chat_uses_custom_model(self, mock_tiktoken, mock_openai):
        """chat() uses the model argument when provided."""
        mock_client = MagicMock()
        mock_openai.return_value = mock_client
        mock_client.chat.completions.create.return_value = self._make_mock_response()
        mock_tiktoken.encoding_for_model.return_value = MagicMock(encode=lambda x: [1, 2])

        provider = OpenAIProvider({"api_key_env": "OPENAI_API_KEY", "model": "gpt-4o-mini"})
        provider.chat([{"role": "user", "content": "hi"}], model="gpt-4")

        mock_client.chat.completions.create.assert_called_once()
        call_kwargs = mock_client.chat.completions.create.call_args
        assert call_kwargs.kwargs["model"] == "gpt-4"

    @patch("ex04.providers.openai_provider.OpenAI")
    @patch("ex04.providers.openai_provider.tiktoken")
    def test_count_tokens(self, mock_tiktoken, mock_openai):
        """count_tokens() returns token count from tiktoken."""
        mock_client = MagicMock()
        mock_openai.return_value = mock_client
        mock_tiktoken.encoding_for_model.return_value = MagicMock(encode=lambda x: [1, 2, 3])

        provider = OpenAIProvider({"api_key_env": "OPENAI_API_KEY", "model": "gpt-4o-mini"})
        count = provider.count_tokens("hello world")

        assert count == 3

    @patch("ex04.providers.openai_provider.OpenAI")
    @patch("ex04.providers.openai_provider.tiktoken")
    def test_chat_empty_response(self, mock_tiktoken, mock_openai):
        """chat() handles empty response gracefully."""
        mock_client = MagicMock()
        mock_openai.return_value = mock_client
        mock_client.chat.completions.create.return_value = MagicMock(
            choices=[], usage=MagicMock(prompt_tokens=0, completion_tokens=0)
        )
        mock_tiktoken.encoding_for_model.return_value = MagicMock(encode=lambda x: [])

        provider = OpenAIProvider({"api_key_env": "OPENAI_API_KEY", "model": "gpt-4o-mini"})
        response = provider.chat([{"role": "user", "content": "hi"}])

        assert response.text == ""
        assert response.input_tokens == 0
        assert response.output_tokens == 0
