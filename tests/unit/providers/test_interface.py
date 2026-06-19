"""Tests for the provider interface — T3.01.

Verifies that ProviderInterface, ProviderResponse, and Message
are properly defined and importable.
"""

from __future__ import annotations

from datetime import datetime

import pytest

from ex04.providers.interface import Message, ProviderInterface, ProviderResponse


class TestMessage:
    """Tests for the Message TypedDict."""

    def test_message_has_role_and_content(self):
        """Message TypedDict has role and content keys."""
        msg: Message = {"role": "user", "content": "hello"}
        assert msg["role"] == "user"
        assert msg["content"] == "hello"

    def test_message_roles(self):
        """Message supports system, user, and assistant roles."""
        for role in ("system", "user", "assistant"):
            msg: Message = {"role": role, "content": "content"}
            assert msg["role"] == role


class TestProviderResponse:
    """Tests for the ProviderResponse dataclass."""

    def test_provider_response_defaults(self):
        """ProviderResponse has sensible defaults."""
        response = ProviderResponse()
        assert response.text == ""
        assert response.input_tokens == 0
        assert response.output_tokens == 0
        assert response.model == ""
        assert response.provider == ""
        assert isinstance(response.timestamp, datetime)

    def test_provider_response_with_values(self):
        """ProviderResponse can be constructed with values."""
        response = ProviderResponse(
            text="Hello",
            input_tokens=10,
            output_tokens=5,
            model="gpt-4o-mini",
            provider="openai",
        )
        assert response.text == "Hello"
        assert response.input_tokens == 10
        assert response.output_tokens == 5
        assert response.model == "gpt-4o-mini"
        assert response.provider == "openai"
        assert isinstance(response.timestamp, datetime)


class TestProviderInterface:
    """Tests for the ProviderInterface ABC."""

    def test_is_abstract(self):
        """ProviderInterface cannot be instantiated directly."""
        with pytest.raises(TypeError):
            ProviderInterface()  # type: ignore[abstract]

    def test_provider_interface_has_chat(self):
        """ProviderInterface has a chat abstract method."""
        assert hasattr(ProviderInterface, "chat")

    def test_provider_interface_has_count_tokens(self):
        """ProviderInterface has a count_tokens abstract method."""
        assert hasattr(ProviderInterface, "count_tokens")
