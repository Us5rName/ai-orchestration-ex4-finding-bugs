"""Tests for shared result types — ProviderResponse, Suspect, Investigation, Pipeline."""

from ex04.shared import (
    ComparisonReport,
    InvestigationResult,
    PipelineResult,
    ProviderResponse,
    Suspect,
    TokenMetrics,
)


class TestProviderResponse:
    """Tests for the ProviderResponse dataclass."""

    def test_provider_response_defaults(self) -> None:
        response = ProviderResponse()
        assert response.text == ""
        assert response.input_tokens == 0
        assert response.output_tokens == 0
        assert response.model == ""
        assert response.provider == ""

    def test_provider_response_with_values(self) -> None:
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


class TestSuspect:
    """Tests for the Suspect dataclass."""

    def test_suspect_requires_location(self) -> None:
        suspect = Suspect(file_path="app.py", line_start=10, line_end=20)
        assert suspect.file_path == "app.py"
        assert suspect.line_start == 10
        assert suspect.line_end == 20
        assert suspect.score == 0.0
        assert suspect.reason == ""

    def test_suspect_with_score_and_reason(self) -> None:
        suspect = Suspect(
            file_path="app.py",
            line_start=10,
            line_end=20,
            score=0.95,
            reason="High centrality",
        )
        assert suspect.score == 0.95
        assert suspect.reason == "High centrality"


class TestInvestigationResult:
    """Tests for the InvestigationResult dataclass."""

    def test_investigation_result_defaults(self) -> None:
        result = InvestigationResult()
        assert result.root_cause == ""
        assert result.suspects == []
        assert result.proposed_fix == ""
        assert result.fix_applied is False
        assert result.test_results == {}
        assert isinstance(result.token_usage, TokenMetrics)


class TestPipelineResult:
    """Tests for the PipelineResult dataclass."""

    def test_pipeline_result_defaults(self) -> None:
        result = PipelineResult()
        assert result.graph_result == ""
        assert result.vault_result == ""
        assert isinstance(result.investigation, InvestigationResult)
        assert isinstance(result.comparison, ComparisonReport)
        assert result.engineering == ""
