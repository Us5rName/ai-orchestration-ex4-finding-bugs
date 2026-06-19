"""Verify every mock implements its interface correctly.

Sanity checks that each mock returns non-None values with correct types.
Ensures the contract layer is properly implemented before Phase 4.
"""

from __future__ import annotations

from pathlib import Path

from ex04.shared.types import (
    Community,
    ComparisonMetrics,
    ComparisonReport,
    Entity,
    GraphData,
    InvestigationResult,
    ProviderResponse,
    Relationship,
    RunMetrics,
    TokenMetrics,
)
from tests.mocks.mock_agent_service import MockAgentService
from tests.mocks.mock_analysis_service import MockAnalysisService
from tests.mocks.mock_comparison_service import MockComparisonService
from tests.mocks.mock_graph_service import MockGraphService
from tests.mocks.mock_provider import MockProvider
from tests.mocks.mock_vault_service import MockVaultService


class TestMockGraphService:
    """Tests for MockGraphService."""

    def test_extract_returns_path(self):
        mock = MockGraphService()
        result = mock.extract("/fake/path")
        assert isinstance(result, Path)

    def test_parse_returns_graph_data(self):
        mock = MockGraphService()
        result = mock.parse(Path("/fake/graph.json"))
        assert isinstance(result, GraphData)
        assert len(result.entities) == 3
        assert len(result.relationships) == 3
        assert len(result.communities) == 1
        assert isinstance(result.entities[0], Entity)
        assert isinstance(result.relationships[0], Relationship)
        assert isinstance(result.communities[0], Community)

    def test_analyze_returns_dict(self):
        mock = MockGraphService()
        graph_data = mock.parse(Path("/fake/graph.json"))
        result = mock.analyze(graph_data)
        assert isinstance(result, dict)
        assert "god_nodes" in result
        assert "centrality_ranking" in result
        assert "communities" in result


class TestMockVaultService:
    """Tests for MockVaultService."""

    def test_build_returns_dict_of_paths(self):
        mock = MockVaultService()
        graph_data = GraphData()
        result = mock.build(graph_data)
        assert isinstance(result, dict)
        for value in result.values():
            assert isinstance(value, Path)

    def test_navigate_returns_list_of_dicts(self):
        mock = MockVaultService()
        result = mock.navigate("test query")
        assert isinstance(result, list)
        assert len(result) > 0
        assert "title" in result[0]
        assert "path" in result[0]
        assert "content" in result[0]

    def test_update_returns_path(self):
        mock = MockVaultService()
        result = mock.update("hot", "Test content")
        assert isinstance(result, Path)


class TestMockAgentService:
    """Tests for MockAgentService."""

    def test_investigate_returns_result(self):
        mock = MockAgentService()
        result = mock.investigate("test bug")
        assert isinstance(result, InvestigationResult)
        assert result.root_cause != ""
        assert isinstance(result.suspects, list)
        assert isinstance(result.token_usage, TokenMetrics)

    def test_get_state_returns_dict(self):
        mock = MockAgentService()
        result = mock.get_state()
        assert isinstance(result, dict)
        assert "bug_report" in result


class TestMockAnalysisService:
    """Tests for MockAnalysisService."""

    def test_reverse_engineer_returns_string(self):
        mock = MockAnalysisService()
        result = mock.reverse_engineer(GraphData())
        assert isinstance(result, str)
        assert "mermaid" in result

    def test_report_returns_string(self):
        mock = MockAnalysisService()
        result = mock.report(InvestigationResult(root_cause="test"))
        assert isinstance(result, str)
        assert "test" in result


class TestMockComparisonService:
    """Tests for MockComparisonService."""

    def test_run_comparison_returns_report(self):
        mock = MockComparisonService()
        result = mock.run_comparison("test bug", [Path("a.py"), Path("b.py")])
        assert isinstance(result, ComparisonReport)
        assert isinstance(result.metrics, ComparisonMetrics)
        assert isinstance(result.metrics.naive, RunMetrics)
        assert isinstance(result.metrics.guided, RunMetrics)
        assert result.token_savings > 0

    def test_comparison_shows_savings(self):
        mock = MockComparisonService()
        result = mock.run_comparison("test bug", [Path("a.py")])
        assert result.metrics.token_savings_pct > 0
        assert result.metrics.file_read_savings_pct > 0


class TestMockProvider:
    """Tests for MockProvider."""

    def test_chat_returns_response(self):
        mock = MockProvider()
        result = mock.chat([{"role": "user", "content": "hello"}])
        assert isinstance(result, ProviderResponse)
        assert result.text != ""
        assert result.input_tokens > 0
        assert result.output_tokens > 0

    def test_count_tokens_returns_int(self):
        mock = MockProvider()
        result = mock.count_tokens("hello world")
        assert isinstance(result, int)
        assert result == 42
