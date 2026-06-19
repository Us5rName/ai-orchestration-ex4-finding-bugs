"""Tests for shared metrics types — TokenMetrics, RunMetrics, Comparison types."""

from ex04.shared import (
    ComparisonMetrics,
    ComparisonReport,
    RunMetrics,
    TokenMetrics,
)


class TestTokenMetrics:
    """Tests for the TokenMetrics dataclass."""

    def test_token_metrics_defaults(self) -> None:
        metrics = TokenMetrics()
        assert metrics.input_tokens == 0
        assert metrics.output_tokens == 0
        assert metrics.total_tokens == 0
        assert metrics.provider == ""
        assert metrics.model == ""

    def test_token_metrics_with_values(self) -> None:
        metrics = TokenMetrics(
            input_tokens=100,
            output_tokens=50,
            provider="openai",
            model="gpt-4o-mini",
        )
        assert metrics.input_tokens == 100
        assert metrics.output_tokens == 50
        assert metrics.total_tokens == 0
        assert metrics.provider == "openai"
        assert metrics.model == "gpt-4o-mini"


class TestRunMetrics:
    """Tests for the RunMetrics dataclass."""

    def test_run_metrics_defaults(self) -> None:
        metrics = RunMetrics()
        assert metrics.tokens_used == 0
        assert metrics.files_read == 0
        assert metrics.iterations == 0
        assert metrics.time_seconds == 0.0
        assert metrics.found_root_cause is False


class TestComparisonMetrics:
    """Tests for the ComparisonMetrics dataclass."""

    def test_comparison_metrics_defaults(self) -> None:
        metrics = ComparisonMetrics()
        assert isinstance(metrics.naive, RunMetrics)
        assert isinstance(metrics.guided, RunMetrics)
        assert metrics.token_savings_pct == 0.0
        assert metrics.file_read_savings_pct == 0.0
        assert metrics.iteration_savings_pct == 0.0


class TestComparisonReport:
    """Tests for the ComparisonReport dataclass."""

    def test_comparison_report_defaults(self) -> None:
        report = ComparisonReport()
        assert isinstance(report.metrics, ComparisonMetrics)
        assert report.narrative == ""
        assert report.token_savings == 0
