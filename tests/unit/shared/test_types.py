"""Tests for shared types — T2.02.

Verifies that all data classes can be constructed with required fields
and that default values are sensible.
"""

from ex04.shared import (
    Community,
    ComparisonMetrics,
    ComparisonReport,
    Entity,
    GraphData,
    InvestigationResult,
    PipelineResult,
    ProviderResponse,
    Relationship,
    RunMetrics,
    Suspect,
    TokenMetrics,
)


class TestEntity:
    """Tests for the Entity dataclass."""

    def test_entity_requires_name_and_kind(self):
        """Entity requires name and kind fields."""
        entity = Entity(name="my_func", kind="function")
        assert entity.name == "my_func"
        assert entity.kind == "function"
        assert entity.file_path == ""
        assert entity.line_range == (0, 0)

    def test_entity_with_all_fields(self):
        """Entity can be constructed with all fields."""
        entity = Entity(name="my_class", kind="class", file_path="app.py", line_range=(1, 50))
        assert entity.name == "my_class"
        assert entity.kind == "class"
        assert entity.file_path == "app.py"
        assert entity.line_range == (1, 50)


class TestRelationship:
    """Tests for the Relationship dataclass."""

    def test_relationship_requires_source_and_target(self):
        """Relationship requires source and target fields."""
        rel = Relationship(source="a", target="b")
        assert rel.source == "a"
        assert rel.target == "b"
        assert rel.type == ""

    def test_relationship_with_type(self):
        """Relationship can include a type."""
        rel = Relationship(source="a", target="b", type="calls")
        assert rel.type == "calls"


class TestCommunity:
    """Tests for the Community dataclass."""

    def test_community_requires_name(self):
        """Community requires a name field."""
        comm = Community(name="cluster_1")
        assert comm.name == "cluster_1"
        assert comm.entities == []
        assert comm.size == 0

    def test_community_with_entities(self):
        """Community can include entities and size."""
        comm = Community(name="cluster_1", entities=["a", "b"], size=2)
        assert comm.entities == ["a", "b"]
        assert comm.size == 2


class TestGraphData:
    """Tests for the GraphData dataclass."""

    def test_graph_data_empty(self):
        """GraphData can be constructed with no data."""
        graph = GraphData()
        assert graph.entities == []
        assert graph.relationships == []
        assert graph.communities == []

    def test_graph_data_with_content(self):
        """GraphData can include entities, relationships, and communities."""
        entity = Entity(name="x", kind="function")
        rel = Relationship(source="x", target="y", type="calls")
        comm = Community(name="c1", entities=["x"], size=1)
        graph = GraphData(entities=[entity], relationships=[rel], communities=[comm])
        assert len(graph.entities) == 1
        assert len(graph.relationships) == 1
        assert len(graph.communities) == 1


class TestTokenMetrics:
    """Tests for the TokenMetrics dataclass."""

    def test_token_metrics_defaults(self):
        """TokenMetrics has sensible defaults."""
        metrics = TokenMetrics()
        assert metrics.input_tokens == 0
        assert metrics.output_tokens == 0
        assert metrics.total_tokens == 0
        assert metrics.provider == ""
        assert metrics.model == ""

    def test_token_metrics_with_values(self):
        """TokenMetrics can be constructed with values."""
        metrics = TokenMetrics(
            input_tokens=100, output_tokens=50, provider="openai", model="gpt-4o-mini"
        )
        assert metrics.input_tokens == 100
        assert metrics.output_tokens == 50
        assert metrics.total_tokens == 0  # not auto-computed
        assert metrics.provider == "openai"
        assert metrics.model == "gpt-4o-mini"


class TestRunMetrics:
    """Tests for the RunMetrics dataclass."""

    def test_run_metrics_defaults(self):
        """RunMetrics has sensible defaults."""
        metrics = RunMetrics()
        assert metrics.tokens_used == 0
        assert metrics.files_read == 0
        assert metrics.iterations == 0
        assert metrics.time_seconds == 0.0
        assert metrics.found_root_cause is False


class TestComparisonMetrics:
    """Tests for the ComparisonMetrics dataclass."""

    def test_comparison_metrics_defaults(self):
        """ComparisonMetrics has sensible defaults."""
        metrics = ComparisonMetrics()
        assert isinstance(metrics.naive, RunMetrics)
        assert isinstance(metrics.guided, RunMetrics)
        assert metrics.token_savings_pct == 0.0
        assert metrics.file_read_savings_pct == 0.0
        assert metrics.iteration_savings_pct == 0.0


class TestComparisonReport:
    """Tests for the ComparisonReport dataclass."""

    def test_comparison_report_defaults(self):
        """ComparisonReport has sensible defaults."""
        report = ComparisonReport()
        assert isinstance(report.metrics, ComparisonMetrics)
        assert report.narrative == ""
        assert report.token_savings == 0


class TestProviderResponse:
    """Tests for the ProviderResponse dataclass."""

    def test_provider_response_defaults(self):
        """ProviderResponse has sensible defaults."""
        response = ProviderResponse()
        assert response.content == ""
        assert response.input_tokens == 0
        assert response.output_tokens == 0
        assert response.model == ""
        assert response.raw == {}

    def test_provider_response_with_values(self):
        """ProviderResponse can be constructed with values."""
        response = ProviderResponse(
            content="Hello", input_tokens=10, output_tokens=5, model="gpt-4o-mini"
        )
        assert response.content == "Hello"
        assert response.input_tokens == 10
        assert response.output_tokens == 5
        assert response.model == "gpt-4o-mini"


class TestSuspect:
    """Tests for the Suspect dataclass."""

    def test_suspect_requires_location(self):
        """Suspect requires file_path, line_start, line_end."""
        suspect = Suspect(file_path="app.py", line_start=10, line_end=20)
        assert suspect.file_path == "app.py"
        assert suspect.line_start == 10
        assert suspect.line_end == 20
        assert suspect.score == 0.0
        assert suspect.reason == ""

    def test_suspect_with_score_and_reason(self):
        """Suspect can include score and reason."""
        suspect = Suspect(
            file_path="app.py", line_start=10, line_end=20, score=0.95, reason="High centrality"
        )
        assert suspect.score == 0.95
        assert suspect.reason == "High centrality"


class TestInvestigationResult:
    """Tests for the InvestigationResult dataclass."""

    def test_investigation_result_defaults(self):
        """InvestigationResult has sensible defaults."""
        result = InvestigationResult()
        assert result.root_cause == ""
        assert result.suspects == []
        assert result.proposed_fix == ""
        assert result.fix_applied is False
        assert result.test_results == {}
        assert isinstance(result.token_usage, TokenMetrics)


class TestPipelineResult:
    """Tests for the PipelineResult dataclass."""

    def test_pipeline_result_defaults(self):
        """PipelineResult has sensible defaults."""
        result = PipelineResult()
        assert result.graph_result == ""
        assert result.vault_result == ""
        assert isinstance(result.investigation, InvestigationResult)
        assert isinstance(result.comparison, ComparisonReport)
        assert result.engineering == ""
