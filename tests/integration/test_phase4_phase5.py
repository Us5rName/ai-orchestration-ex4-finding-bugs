"""Phase 4 → Phase 5 integration tests.

Verifies the real Phase 4/5 boundary without external API access.
Concrete SDK orchestration is exercised; only provider/LLM calls are
replaced with deterministic fakes.

No API key or network call is required.
"""

from __future__ import annotations

from pathlib import Path

import pytest

from ex04.sdk._comparison_inputs import discover_source_files, resolve_vault_dir
from ex04.sdk.sdk import Ex04SDK
from ex04.services.agent.nodes.inspect import CodeInspectionNode
from ex04.shared.types import GraphData
from ex04.shared.types_metrics import ComparisonReport
from ex04.shared.types_results import Suspect
from tests.mocks.mock_agent_service import MockAgentService
from tests.mocks.mock_analysis_service import MockAnalysisService
from tests.mocks.mock_graph_service import MockGraphService
from tests.mocks.mock_vault_service import MockVaultService

# ---------------------------------------------------------------------------
# Recording comparison service — captures real inputs for assertion
# ---------------------------------------------------------------------------


class RecordingComparisonService:
    """Captures run_comparison arguments for assertion."""

    def __init__(self) -> None:
        self.calls: list[dict] = []

    def run_comparison(
        self,
        bug_report: str,
        source_files: list[Path],
        graph_data: GraphData | None = None,
        vault_path: Path | None = None,
    ) -> ComparisonReport:
        """Record inputs and return a minimal valid report."""
        from ex04.shared.types import ComparisonMetrics, RunMetrics

        self.calls.append(
            {
                "bug_report": bug_report,
                "source_files": list(source_files),
                "graph_data": graph_data,
                "vault_path": vault_path,
            }
        )
        metrics = ComparisonMetrics(
            naive=RunMetrics(tokens_used=100, files_read=2, iterations=1),
            guided=RunMetrics(tokens_used=50, files_read=1, iterations=1),
            token_savings_pct=50.0,
            file_read_savings_pct=50.0,
            iteration_savings_pct=0.0,
        )
        return ComparisonReport(metrics=metrics, narrative="integration test", token_savings=50)


@pytest.fixture
def codebase(tmp_path: Path) -> Path:
    """Seed a minimal Python codebase in a temp directory."""
    (tmp_path / "main.py").write_text("def main(): pass\n", encoding="utf-8")
    (tmp_path / "utils.py").write_text("def helper(): return 1\n", encoding="utf-8")
    return tmp_path


@pytest.fixture
def recorder() -> RecordingComparisonService:
    return RecordingComparisonService()


@pytest.fixture
def sdk(recorder: RecordingComparisonService) -> Ex04SDK:
    return Ex04SDK(
        graph=MockGraphService(),
        vault=MockVaultService(),
        agent=MockAgentService(),
        comparison=recorder,
        analysis=MockAnalysisService(),
    )


# ---------------------------------------------------------------------------
# 1. SDK comparison orchestration supplies nonempty source files
# ---------------------------------------------------------------------------


class TestCompareTargetIntegration:
    """compare_target passes real inputs to comparison."""

    def test_nonempty_source_files_supplied(
        self, sdk: Ex04SDK, recorder: RecordingComparisonService, codebase: Path
    ) -> None:
        sdk.compare_target(codebase, "crash on startup")
        assert recorder.calls, "compare_target must invoke run_comparison"
        assert recorder.calls[0]["source_files"], "source_files must be nonempty"

    def test_source_files_are_real_python_files(
        self, sdk: Ex04SDK, recorder: RecordingComparisonService, codebase: Path
    ) -> None:
        sdk.compare_target(codebase, "crash")
        for path in recorder.calls[0]["source_files"]:
            assert path.suffix == ".py"
            assert path.is_file()

    def test_graph_data_reaches_comparison(
        self, sdk: Ex04SDK, recorder: RecordingComparisonService, codebase: Path
    ) -> None:
        sdk.compare_target(codebase, "crash")
        gd = recorder.calls[0]["graph_data"]
        assert isinstance(gd, GraphData)
        assert gd.entities

    def test_vault_path_reaches_comparison(
        self, sdk: Ex04SDK, recorder: RecordingComparisonService, codebase: Path
    ) -> None:
        sdk.compare_target(codebase, "crash")
        assert recorder.calls[0]["vault_path"] is not None

    def test_bug_report_forwarded(
        self, sdk: Ex04SDK, recorder: RecordingComparisonService, codebase: Path
    ) -> None:
        sdk.compare_target(codebase, "my-specific-bug")
        assert recorder.calls[0]["bug_report"] == "my-specific-bug"

    def test_result_type(
        self, sdk: Ex04SDK, codebase: Path
    ) -> None:
        result = sdk.compare_target(codebase, "crash")
        assert isinstance(result, ComparisonReport)


# ---------------------------------------------------------------------------
# 2. full_pipeline integration
# ---------------------------------------------------------------------------


class TestFullPipelineIntegration:
    """full_pipeline passes real artifacts through the whole chain."""

    def test_nonempty_sources_in_full_pipeline(
        self, sdk: Ex04SDK, recorder: RecordingComparisonService, codebase: Path
    ) -> None:
        sdk.full_pipeline(str(codebase), "crash")
        assert recorder.calls[0]["source_files"]

    def test_vault_path_in_full_pipeline(
        self, sdk: Ex04SDK, recorder: RecordingComparisonService, codebase: Path
    ) -> None:
        sdk.full_pipeline(str(codebase), "crash")
        assert recorder.calls[0]["vault_path"] is not None

    def test_bug_report_md_in_result(
        self, sdk: Ex04SDK, codebase: Path
    ) -> None:
        result = sdk.full_pipeline(str(codebase), "crash")
        assert isinstance(result.bug_report_md, str)
        assert result.bug_report_md

    def test_graph_data_in_full_pipeline(
        self, sdk: Ex04SDK, recorder: RecordingComparisonService, codebase: Path
    ) -> None:
        sdk.full_pipeline(str(codebase), "crash")
        assert isinstance(recorder.calls[0]["graph_data"], GraphData)


# ---------------------------------------------------------------------------
# 3. Cumulative files_read across retry cycles
# ---------------------------------------------------------------------------


class TestCumulativeFilesReadIntegration:
    """CodeInspectionNode accumulates files_read across retries."""

    def test_two_passes_accumulate(self, tmp_path: Path) -> None:
        (tmp_path / "src").mkdir()
        (tmp_path / "src" / "a.py").write_text("x=1\n", encoding="utf-8")
        node = CodeInspectionNode(target_path=tmp_path)
        suspect = Suspect(file_path="src/a.py", line_start=1, line_end=1, score=0.9)

        state_after_first = node({"suspects": [suspect]})
        assert state_after_first["files_read"] == 1

        state_after_second = node(state_after_first)
        assert state_after_second["files_read"] == 2

    def test_three_retries_accumulate(self, tmp_path: Path) -> None:
        (tmp_path / "m.py").write_text("m=0\n", encoding="utf-8")
        node = CodeInspectionNode(target_path=tmp_path)
        suspect = Suspect(file_path="m.py", line_start=1, line_end=1, score=0.8)

        state: dict = {"suspects": [suspect]}
        for expected in (1, 2, 3):
            state = node(state)
            assert state["files_read"] == expected


# ---------------------------------------------------------------------------
# 4. Source discovery determinism
# ---------------------------------------------------------------------------


class TestSourceDiscoveryIntegration:
    """discover_source_files is deterministic and excludes generated dirs."""

    def test_excludes_venv_from_discovery(self, tmp_path: Path) -> None:
        (tmp_path / "real.py").write_text("x=1", encoding="utf-8")
        venv = tmp_path / ".venv" / "lib"
        venv.mkdir(parents=True)
        (venv / "hidden.py").write_text("x=2", encoding="utf-8")
        result = discover_source_files(tmp_path)
        for f in result:
            assert ".venv" not in f.parts

    def test_deterministic_across_calls(self, codebase: Path) -> None:
        first = discover_source_files(codebase)
        second = discover_source_files(codebase)
        assert first == second

    def test_resolve_vault_dir_prefers_index(self) -> None:
        vault = {
            "index": Path("/tmp/vault/index.md"),
            "hot": Path("/tmp/vault/hot.md"),
        }
        result = resolve_vault_dir(vault)
        assert result == Path("/tmp/vault")

    def test_resolve_vault_dir_fallback(self) -> None:
        vault = {"entities": Path("/tmp/vault2/entities.md")}
        result = resolve_vault_dir(vault)
        assert result == Path("/tmp/vault2")

    def test_resolve_vault_dir_empty(self) -> None:
        assert resolve_vault_dir({}) is None
