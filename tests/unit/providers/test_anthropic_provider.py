"""Tests for the Anthropic Provider — T3.03.

Uses mocked Anthropic client — no real API calls.
"""

from __future__ import annotations

from unittest.mock import MagicMock, patch

from ex04.providers.anthropic_provider import AnthropicProvider
from ex04.providers.interface import ProviderResponse


class TestAnthropicProvider:
    """Tests for AnthropicProvider."""

    def _make_mock_response(self):
        """Create a mock Anthropic API response."""
        content_block = MagicMock()
        content_block.text = "Mocked response"
        usage = MagicMock(input_tokens=8, output_tokens=4)
        return MagicMock(content=[content_block], usage=usage)

    @patch("ex04.providers.anthropic_provider.Anthropic")
    def test_chat_returns_provider_response(self, mock_anthropic):
        """chat() returns a ProviderResponse with correct fields."""
        mock_client = MagicMock()
        mock_anthropic.return_value = mock_client
        mock_client.messages.create.return_value = self._make_mock_response()
        mock_client.count_tokens.return_value = 5

        provider = AnthropicProvider(
            {"api_key_env": "ANTHROPIC_API_KEY", "model": "claude-sonnet-4-20250514"}
        )
        response = provider.chat([{"role": "user", "content": "hello"}])

        assert isinstance(response, ProviderResponse)
        assert response.text == "Mocked response"
        assert response.input_tokens == 8
        assert response.output_tokens == 4
        assert response.model == "claude-sonnet-4-20250514"
        assert response.provider == "anthropic"

    @patch("ex04.providers.anthropic_provider.Anthropic")
    def test_chat_handles_system_message(self, mock_anthropic):
        """chat() extracts and passes system message separately."""
        mock_client = MagicMock()
        mock_anthropic.return_value = mock_client
        mock_client.messages.create.return_value = self._make_mock_response()
        mock_client.count_tokens.return_value = 5

        provider = AnthropicProvider(
            {"api_key_env": "ANTHROPIC_API_KEY", "model": "claude-sonnet-4-20250514"}
        )
        messages = [
            {"role": "system", "content": "You are helpful."},
            {"role": "user", "content": "hello"},
        ]
        provider.chat(messages)

        call_kwargs = mock_client.messages.create.call_args.kwargs
        assert call_kwargs["system"] == "You are helpful."
        assert len(call_kwargs["messages"]) == 1
        assert call_kwargs["messages"][0]["role"] == "user"

    @patch("ex04.providers.anthropic_provider.Anthropic")
    def test_count_tokens(self, mock_anthropic):
        """count_tokens() uses the messages.count_tokens endpoint."""
        mock_client = MagicMock()
        mock_anthropic.return_value = mock_client
        mock_client.messages.count_tokens.return_value = MagicMock(input_tokens=42)

        provider = AnthropicProvider(
            {"api_key_env": "ANTHROPIC_API_KEY", "model": "claude-sonnet-4-20250514"}
        )
        count = provider.count_tokens("hello world")

        assert count == 42
        mock_client.messages.count_tokens.assert_called_once_with(
            model="claude-sonnet-4-20250514",
            messages=[{"role": "user", "content": "hello world"}],
        )

    @patch("ex04.providers.anthropic_provider.Anthropic")
    def test_chat_passes_max_tokens(self, mock_anthropic):
        """chat() always sends the required max_tokens to the Messages API."""
        mock_client = MagicMock()
        mock_anthropic.return_value = mock_client
        mock_client.messages.create.return_value = self._make_mock_response()

        provider = AnthropicProvider(
            {"api_key_env": "ANTHROPIC_API_KEY", "model": "claude-sonnet-4-20250514", "max_tokens": 256}
        )
        provider.chat([{"role": "user", "content": "hello"}])

        call_kwargs = mock_client.messages.create.call_args.kwargs
        assert call_kwargs["max_tokens"] == 256
        # No system message → 'system' must be omitted, not passed as None.
        assert "system" not in call_kwargs

    @patch("ex04.providers.anthropic_provider.Anthropic")
    def test_chat_empty_response(self, mock_anthropic):
        """chat() handles empty response gracefully."""
        mock_client = MagicMock()
        mock_anthropic.return_value = mock_client
        mock_client.messages.create.return_value = MagicMock(
            content=[], usage=MagicMock(input_tokens=0, output_tokens=0)
        )
        mock_client.count_tokens.return_value = 0

        provider = AnthropicProvider(
            {"api_key_env": "ANTHROPIC_API_KEY", "model": "claude-sonnet-4-20250514"}
        )
        response = provider.chat([{"role": "user", "content": "hi"}])

        assert response.text == ""
        assert response.input_tokens == 0
        assert response.output_tokens == 0
