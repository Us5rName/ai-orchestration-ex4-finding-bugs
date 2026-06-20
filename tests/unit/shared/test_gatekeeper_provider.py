"""Tests for Gatekeeper provider configuration and caching."""

from __future__ import annotations

import json
import tempfile
from unittest.mock import MagicMock, patch

from ex04.shared.gatekeeper import ApiGatekeeper
from ex04.shared.types_results import ProviderResponse


def _fast_retry_path() -> str:
    """Return a temp rate-limits file with zero retry delay."""
    tmp_path = tempfile.mktemp(suffix=".json")
    with open(tmp_path, "w") as tmp:
        json.dump(
            {
                "openai": {
                    "requests_per_minute": 60,
                    "requests_per_day": 10000,
                    "retry_attempts": 3,
                    "retry_delay_seconds": 1,
                }
            },
            tmp,
        )
    return tmp_path


@patch("ex04.providers.factory.ProviderFactory.create")
def test_send_honors_provider_config(mock_create: MagicMock) -> None:
    """Provider config is passed through factory and chat model selection."""
    mock_provider = MagicMock()
    mock_provider.chat.return_value = ProviderResponse(text="ok", provider="openai")
    mock_create.return_value = mock_provider

    gatekeeper = ApiGatekeeper(
        rate_limits_path=_fast_retry_path(),
        provider_configs={
            "openai": {"model": "gpt-4o", "base_url": "http://proxy", "max_tokens": 100}
        },
    )
    gatekeeper.send("openai", [{"role": "user", "content": "hi"}])

    name, config = mock_create.call_args.args
    assert name == "openai"
    assert config["base_url"] == "http://proxy"
    assert config["model"] == "gpt-4o"
    assert config["api_key_env"] == "OPENAI_API_KEY"
    assert mock_provider.chat.call_args.kwargs["model"] == "gpt-4o"


@patch("ex04.providers.factory.ProviderFactory.create")
def test_send_caches_provider_across_calls(mock_create: MagicMock) -> None:
    """Provider instances are cached between calls."""
    mock_provider = MagicMock()
    mock_provider.chat.return_value = ProviderResponse(text="ok", provider="openai")
    mock_create.return_value = mock_provider

    gatekeeper = ApiGatekeeper(rate_limits_path=_fast_retry_path())
    gatekeeper.send("openai", [{"role": "user", "content": "a"}])
    gatekeeper.send("openai", [{"role": "user", "content": "b"}])

    assert mock_create.call_count == 1
    assert mock_provider.chat.call_count == 2
    assert gatekeeper.get_queue_status()["queue_size"] == 0
