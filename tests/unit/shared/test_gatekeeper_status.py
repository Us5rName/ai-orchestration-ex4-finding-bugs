"""Tests for ApiGatekeeper call log and queue status."""

from __future__ import annotations

from datetime import datetime
from unittest.mock import MagicMock, patch

from ex04.shared.gatekeeper import ApiGatekeeper
from ex04.shared.types_results import ProviderResponse


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
