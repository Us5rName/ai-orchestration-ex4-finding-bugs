"""Tests for MockComparisonService and MockProvider."""

from __future__ import annotations

from pathlib import Path

from ex04.shared.types import (
    ComparisonMetrics,
    ComparisonReport,
    ProviderResponse,
    RunMetrics,
)
from tests.mocks.mock_comparison_service import MockComparisonService
from tests.mocks.mock_provider import MockProvider


class TestMockComparisonService:
    """Tests for MockComparisonService."""

    def test_run_comparison_returns_report(self) -> None:
        mock = MockComparisonService()
        result = mock.run_comparison("test bug", [Path("a.py"), Path("b.py")])
        assert isinstance(result, ComparisonReport)
        assert isinstance(result.metrics, ComparisonMetrics)
        assert isinstance(result.metrics.naive, RunMetrics)
        assert isinstance(result.metrics.guided, RunMetrics)
        assert result.token_savings > 0

    def test_comparison_shows_savings(self) -> None:
        mock = MockComparisonService()
        result = mock.run_comparison("test bug", [Path("a.py")])
        assert result.metrics.token_savings_pct > 0
        assert result.metrics.file_read_savings_pct > 0


class TestMockProvider:
    """Tests for MockProvider."""

    def test_chat_returns_response(self) -> None:
        mock = MockProvider()
        result = mock.chat([{"role": "user", "content": "hello"}])
        assert isinstance(result, ProviderResponse)
        assert result.text != ""
        assert result.input_tokens > 0
        assert result.output_tokens > 0

    def test_count_tokens_returns_int(self) -> None:
        mock = MockProvider()
        result = mock.count_tokens("hello world")
        assert isinstance(result, int)
        assert result == 42
