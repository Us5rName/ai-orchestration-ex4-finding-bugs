"""Tests for the ProviderFactory — T3.04.

Verifies that ProviderFactory correctly creates provider instances
and validates API key requirements.
"""

from __future__ import annotations

import os
from unittest.mock import MagicMock, patch

import pytest

from ex04.providers.factory import ProviderFactory
from ex04.providers.interface import ProviderInterface


class TestProviderFactory:
    """Tests for ProviderFactory."""

    def test_create_openai(self):
        """Factory creates OpenAIProvider for 'openai' name."""
        with patch.dict(os.environ, {"OPENAI_API_KEY": "test-key"}, clear=False):
            provider = ProviderFactory.create("openai", {"api_key_env": "OPENAI_API_KEY"})
            assert isinstance(provider, ProviderInterface)

    def test_create_anthropic(self):
        """Factory creates AnthropicProvider for 'anthropic' name."""
        with patch.dict(os.environ, {"ANTHROPIC_API_KEY": "test-key"}, clear=False):
            provider = ProviderFactory.create("anthropic", {"api_key_env": "ANTHROPIC_API_KEY"})
            assert isinstance(provider, ProviderInterface)

    def test_create_unknown_provider_raises_value_error(self):
        """Factory raises ValueError for unknown provider name."""
        with pytest.raises(ValueError, match="Unknown provider"):
            ProviderFactory.create("unknown", {})

    def test_create_missing_api_key_raises_runtime_error(self):
        """Factory raises RuntimeError when API key env var is missing."""
        with (
            patch.dict(os.environ, {}, clear=True),
            pytest.raises(RuntimeError, match="Required API key"),
        ):
            ProviderFactory.create("openai", {"api_key_env": "MISSING_KEY"})

    @patch("ex04.providers.openai_provider.OpenAI")
    @patch("ex04.providers.openai_provider.tiktoken")
    def test_create_without_api_key_env(self, mock_tiktoken, mock_openai):
        """Factory works when config has no api_key_env."""
        mock_openai.return_value = MagicMock()
        mock_tiktoken.encoding_for_model.return_value = MagicMock(encode=lambda x: [])
        provider = ProviderFactory.create("openai", {})
        assert isinstance(provider, ProviderInterface)

    def test_registry_contains_providers(self):
        """Factory registry contains openai and anthropic."""
        assert "openai" in ProviderFactory._registry
        assert "anthropic" in ProviderFactory._registry
