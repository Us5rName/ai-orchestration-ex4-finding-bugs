"""Tests for ApiGatekeeper.send(), call log, and queue status — T4.002."""

from __future__ import annotations

import json
import tempfile
from datetime import datetime
from unittest.mock import MagicMock, patch

import pytest

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


class TestGatekeeperSend:
    """Tests for ApiGatekeeper.send() method."""

    @patch("ex04.providers.factory.ProviderFactory.create")
    def test_send_calls_provider_chat(self, mock_create: MagicMock) -> None:
        mock_provider = MagicMock()
        mock_provider.chat.return_value = ProviderResponse(
            text="Hello",
            input_tokens=10,
            output_tokens=5,
            model="gpt-4o-mini",
            provider="openai",
        )
        mock_create.return_value = mock_provider

        gatekeeper = ApiGatekeeper(rate_limits_path=_fast_retry_path())
        messages = [{"role": "user", "content": "Hello"}]
        response = gatekeeper.send("openai", messages)

        mock_create.assert_called_once()
        mock_provider.chat.assert_called_once()
        assert response.text == "Hello"

    @patch("ex04.providers.factory.ProviderFactory.create")
    def test_send_returns_provider_response(self, mock_create: MagicMock) -> None:
        mock_provider = MagicMock()
        expected_response = ProviderResponse(
            text="Response text",
            input_tokens=20,
            output_tokens=10,
            model="gpt-4o-mini",
            provider="openai",
            timestamp=datetime.now(),
        )
        mock_provider.chat.return_value = expected_response
        mock_create.return_value = mock_provider

        gatekeeper = ApiGatekeeper(rate_limits_path=_fast_retry_path())
        response = gatekeeper.send("openai", [{"role": "user", "content": "Test"}])

        assert response.text == "Response text"
        assert response.input_tokens == 20
        assert response.output_tokens == 10
        assert response.provider == "openai"

    @patch("ex04.providers.factory.ProviderFactory.create")
    def test_send_logs_call(self, mock_create: MagicMock) -> None:
        mock_provider = MagicMock()
        mock_provider.chat.return_value = ProviderResponse(
            text="OK",
            input_tokens=5,
            output_tokens=3,
            model="gpt-4o-mini",
            provider="openai",
        )
        mock_create.return_value = mock_provider

        gatekeeper = ApiGatekeeper(rate_limits_path=_fast_retry_path())
        gatekeeper.send("openai", [{"role": "user", "content": "Test"}])

        log = gatekeeper.get_call_log()
        assert len(log) == 1
        assert log[0]["provider"] == "openai"
        assert log[0]["status"] == "success"

    @patch("ex04.providers.factory.ProviderFactory.create")
    def test_send_handles_provider_error(self, mock_create: MagicMock) -> None:
        mock_provider = MagicMock()
        mock_provider.chat.side_effect = Exception("API error")
        mock_create.return_value = mock_provider

        gatekeeper = ApiGatekeeper(rate_limits_path=_fast_retry_path())
        with pytest.raises(Exception, match="API error"):
            gatekeeper.send("openai", [{"role": "user", "content": "Test"}])


class TestGatekeeperCallLog:
    """Tests for ApiGatekeeper.get_call_log() method."""

    @patch("ex04.providers.factory.ProviderFactory.create")
    def test_get_call_log_returns_list(self, mock_create: MagicMock) -> None:
        mock_provider = MagicMock()
        mock_provider.chat.return_value = ProviderResponse(
            text="OK",
            input_tokens=1,
            output_tokens=1,
            model="gpt-4o-mini",
            provider="openai",
        )
        mock_create.return_value = mock_provider

        gatekeeper = ApiGatekeeper(rate_limits_path="")
        assert isinstance(gatekeeper.get_call_log(), list)
        assert len(gatekeeper.get_call_log()) == 0

    @patch("ex04.providers.factory.ProviderFactory.create")
    def test_get_call_log_contains_timestamp(self, mock_create: MagicMock) -> None:
        mock_provider = MagicMock()
        mock_provider.chat.return_value = ProviderResponse(
            text="OK",
            input_tokens=1,
            output_tokens=1,
            model="gpt-4o-mini",
            provider="openai",
        )
        mock_create.return_value = mock_provider

        gatekeeper = ApiGatekeeper(rate_limits_path="")
        gatekeeper.send("openai", [{"role": "user", "content": "Test"}])

        log = gatekeeper.get_call_log()
        assert "timestamp" in log[0]
        assert isinstance(log[0]["timestamp"], datetime)


class TestGatekeeperQueueStatus:
    """Tests for ApiGatekeeper.get_queue_status() method."""

    def test_get_queue_status_returns_dict(self) -> None:
        gatekeeper = ApiGatekeeper(rate_limits_path="")
        status = gatekeeper.get_queue_status()
        assert isinstance(status, dict)

    def test_get_queue_status_has_required_keys(self) -> None:
        gatekeeper = ApiGatekeeper(rate_limits_path="")
        status = gatekeeper.get_queue_status()
        assert "queue_size" in status
        assert "is_processing" in status
        assert "rate_limited" in status

    def test_get_queue_status_empty_queue(self) -> None:
        gatekeeper = ApiGatekeeper(rate_limits_path="")
        status = gatekeeper.get_queue_status()
        assert status["queue_size"] == 0
        assert status["is_processing"] is False
