"""Tests for ProviderPool — caching and per-provider config — T4.002."""

from __future__ import annotations

from unittest.mock import MagicMock, patch

from ex04.shared.provider_pool import ProviderPool


class TestProviderPool:
    """Tests for lazy creation, caching, and config resolution."""

    @patch("ex04.providers.factory.ProviderFactory.create")
    def test_get_caches_instance(self, mock_create: MagicMock) -> None:
        mock_create.return_value = MagicMock()
        pool = ProviderPool()
        first = pool.get("openai")
        second = pool.get("openai")
        assert first is second
        assert mock_create.call_count == 1

    @patch("ex04.providers.factory.ProviderFactory.create")
    def test_get_defaults_api_key_env(self, mock_create: MagicMock) -> None:
        mock_create.return_value = MagicMock()
        ProviderPool().get("anthropic")
        _, config = mock_create.call_args.args
        assert config["api_key_env"] == "ANTHROPIC_API_KEY"

    @patch("ex04.providers.factory.ProviderFactory.create")
    def test_get_passes_configured_values(self, mock_create: MagicMock) -> None:
        mock_create.return_value = MagicMock()
        pool = ProviderPool({"openai": {"model": "gpt-4o", "base_url": "http://proxy"}})
        pool.get("openai")
        _, config = mock_create.call_args.args
        assert config["model"] == "gpt-4o"
        assert config["base_url"] == "http://proxy"

    def test_model_for(self) -> None:
        pool = ProviderPool({"openai": {"model": "gpt-4o"}})
        assert pool.model_for("openai") == "gpt-4o"
        assert pool.model_for("anthropic") is None
