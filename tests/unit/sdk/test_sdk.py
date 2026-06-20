"""Unit tests for Ex04SDK — all services mocked, no real API calls."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from ex04.sdk import Ex04SDK
from ex04.shared.types import GraphData
from ex04.shared.types_metrics import ComparisonReport
from ex04.shared.types_results import InvestigationResult, PipelineResult
from tests.mocks.mock_agent_service import MockAgentService
from tests.mocks.mock_analysis_service import MockAnalysisService
from tests.mocks.mock_comparison_service import MockComparisonService
from tests.mocks.mock_graph_service import MockGraphService
from tests.mocks.mock_vault_service import MockVaultService


@pytest.fixture
def sdk() -> Ex04SDK:
    """An SDK wired with the standard mock services."""
    return Ex04SDK(
        graph=MockGraphService(),
        vault=MockVaultService(),
        agent=MockAgentService(),
        comparison=MockComparisonService(),
        analysis=MockAnalysisService(),
        config={"provider": {"name": "openai"}},
    )


def test_run_graphify_returns_graph_data(sdk: Ex04SDK) -> None:
    result = sdk.run_graphify("/some/path")
    assert isinstance(result, GraphData)
    assert result.entities


def test_build_vault_returns_note_paths(sdk: Ex04SDK) -> None:
    graph = sdk.run_graphify("/some/path")
    notes = sdk.build_vault(graph)
    assert "index" in notes
    assert isinstance(notes["index"], Path)


def test_investigate_bug_returns_result(sdk: Ex04SDK) -> None:
    result = sdk.investigate_bug("crash on startup")
    assert isinstance(result, InvestigationResult)


def test_investigate_bug_passes_optional_paths(sdk: Ex04SDK) -> None:
    result = sdk.investigate_bug(
        "crash", graph_path=Path("/g.json"), vault_path=Path("/vault")
    )
    assert isinstance(result, InvestigationResult)


def test_run_comparison_returns_report(sdk: Ex04SDK) -> None:
    report = sdk.run_comparison("bug", [Path("a.py")])
    assert isinstance(report, ComparisonReport)


def test_reverse_engineer_returns_text(sdk: Ex04SDK) -> None:
    text = sdk.reverse_engineer("/some/path")
    assert isinstance(text, str)
    assert text


def test_full_pipeline_aggregates_all_stages(sdk: Ex04SDK) -> None:
    result = sdk.full_pipeline("/some/path", "bug report")
    assert isinstance(result, PipelineResult)
    assert result.graph_result
    assert result.vault_result
    assert isinstance(result.investigation, InvestigationResult)
    assert isinstance(result.comparison, ComparisonReport)
    assert isinstance(result.engineering, str)


def test_from_config_loads_json_and_attempts_wiring(tmp_path: Path) -> None:
    """from_config reads the file, then hits the Phase 4 integration point."""
    cfg = tmp_path / "setup.json"
    cfg.write_text(json.dumps({"provider": {"name": "openai"}}), encoding="utf-8")
    with pytest.raises(NotImplementedError):
        Ex04SDK.from_config(str(cfg))


def test_from_config_missing_file_raises(tmp_path: Path) -> None:
    with pytest.raises(FileNotFoundError):
        Ex04SDK.from_config(str(tmp_path / "nope.json"))
