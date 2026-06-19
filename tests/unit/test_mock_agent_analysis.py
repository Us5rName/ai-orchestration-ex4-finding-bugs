"""Tests for MockAgentService and MockAnalysisService."""

from __future__ import annotations

from ex04.shared.types import (
    GraphData,
    InvestigationResult,
    TokenMetrics,
)
from tests.mocks.mock_agent_service import MockAgentService
from tests.mocks.mock_analysis_service import MockAnalysisService


class TestMockAgentService:
    """Tests for MockAgentService."""

    def test_investigate_returns_result(self) -> None:
        mock = MockAgentService()
        result = mock.investigate("test bug")
        assert isinstance(result, InvestigationResult)
        assert result.root_cause != ""
        assert isinstance(result.suspects, list)
        assert isinstance(result.token_usage, TokenMetrics)

    def test_get_state_returns_dict(self) -> None:
        mock = MockAgentService()
        result = mock.get_state()
        assert isinstance(result, dict)
        assert "bug_report" in result


class TestMockAnalysisService:
    """Tests for MockAnalysisService."""

    def test_reverse_engineer_returns_string(self) -> None:
        mock = MockAnalysisService()
        result = mock.reverse_engineer(GraphData())
        assert isinstance(result, str)
        assert "mermaid" in result

    def test_report_returns_string(self) -> None:
        mock = MockAnalysisService()
        result = mock.report(InvestigationResult(root_cause="test"))
        assert isinstance(result, str)
        assert "test" in result
