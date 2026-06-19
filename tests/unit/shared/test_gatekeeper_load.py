"""Tests for ApiGatekeeper rate limit loading and integration — T4.002."""

from __future__ import annotations

import json
import os
import tempfile
from pathlib import Path

import pytest

from ex04.shared.gatekeeper import ApiGatekeeper


class TestGatekeeperLoadRateLimits:
    """Tests for rate limit loading."""

    def test_load_rate_limits_from_file(self) -> None:
        with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as tmp:
            json.dump(
                {
                    "openai": {
                        "requests_per_minute": 10,
                        "requests_per_day": 100,
                        "retry_attempts": 2,
                        "retry_delay_seconds": 1,
                    }
                },
                tmp,
            )
            tmp_path = tmp.name

        try:
            gatekeeper = ApiGatekeeper(rate_limits_path=tmp_path)
            config = gatekeeper._limiter.get_config("openai")
            assert config["requests_per_minute"] == 10
            assert config["retry_attempts"] == 2
        finally:
            os.unlink(tmp_path)

    def test_load_missing_rate_limits_file(self) -> None:
        with pytest.raises(FileNotFoundError):
            ApiGatekeeper(rate_limits_path="/nonexistent/path.json")

    def test_load_default_rate_limits(self) -> None:
        gatekeeper = ApiGatekeeper(rate_limits_path="")
        config = gatekeeper._limiter.get_config("openai")
        assert config["requests_per_minute"] == 60

    def test_load_malformed_json(self) -> None:
        with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as tmp:
            tmp.write("{invalid json}")
            tmp_path = tmp.name

        try:
            with pytest.raises(ValueError):
                ApiGatekeeper(rate_limits_path=tmp_path)
        finally:
            os.unlink(tmp_path)


class TestGatekeeperIntegration:
    """Integration tests using actual config files."""

    def test_load_rate_limits_from_actual_config(self) -> None:
        config_path = Path(__file__).parent.parent.parent.parent / "config" / "rate_limits.json"
        if not config_path.exists():
            pytest.skip("config/rate_limits.json not found")

        gatekeeper = ApiGatekeeper(rate_limits_path=str(config_path))
        assert gatekeeper._limiter.get_config("openai")["requests_per_minute"] > 0
        assert gatekeeper._limiter.get_config("anthropic")["requests_per_minute"] > 0
