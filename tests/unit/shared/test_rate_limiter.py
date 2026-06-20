"""Tests for RateLimiter — recording vs non-recording checks — T4.002."""

from __future__ import annotations

import json
import tempfile

from ex04.shared.rate_limiter import RateLimiter


def _limiter(rpm: int = 60, rpd: int = 1000) -> RateLimiter:
    """Build a RateLimiter configured for the 'openai' provider."""
    rl = RateLimiter()
    tmp_path = tempfile.mktemp(suffix=".json")
    with open(tmp_path, "w") as tmp:
        json.dump(
            {
                "openai": {
                    "requests_per_minute": rpm,
                    "requests_per_day": rpd,
                    "retry_attempts": 3,
                    "retry_delay_seconds": 1,
                }
            },
            tmp,
        )
    rl.load(tmp_path)
    return rl


class TestRateLimiter:
    """Tests for the consuming and non-consuming limit checks."""

    def test_is_within_limit_records_and_blocks_at_cap(self) -> None:
        rl = _limiter(rpm=2)
        assert rl.is_within_limit("openai") is True
        assert rl.is_within_limit("openai") is True
        assert rl.is_within_limit("openai") is False

    def test_is_currently_limited_does_not_record(self) -> None:
        rl = _limiter(rpm=1)
        # Polling status many times must not consume the single slot.
        for _ in range(10):
            assert rl.is_currently_limited("openai") is False
        assert rl.is_within_limit("openai") is True
        assert rl.is_currently_limited("openai") is True

    def test_is_any_limited_does_not_consume_budget(self) -> None:
        rl = _limiter(rpm=1)
        for _ in range(10):
            rl.is_any_limited()
        # The real request slot survived all the status polls.
        assert rl.is_within_limit("openai") is True

    def test_get_config_merges_partial_entry(self) -> None:
        rl = RateLimiter()
        tmp_path = tempfile.mktemp(suffix=".json")
        with open(tmp_path, "w") as tmp:
            json.dump({"openai": {"requests_per_minute": 5}}, tmp)
        rl.load(tmp_path)

        config = rl.get_config("openai")
        assert config["requests_per_minute"] == 5
        assert config["requests_per_day"] == 10000  # default filled in
        # A partial config must not raise on a limit check.
        assert rl.is_within_limit("openai") is True

    def test_get_config_unknown_provider_uses_defaults(self) -> None:
        rl = RateLimiter()
        assert rl.get_config("mystery")["requests_per_minute"] == 60
