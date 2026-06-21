"""Tests for ComparisonService facade."""

import json
from pathlib import Path

import pytest

from ex04.services.comparison.fairness import FairnessViolationError
from ex04.services.comparison.service import ComparisonService
from ex04.shared.types import Entity, GraphData, Relationship
from ex04.shared.types_experiment import ComparisonOutcome
from ex04.shared.types_request import ComparisonRequest
from ex04.shared.types_results import ProviderResponse


class FakeGatekeeper:
    """Gatekeeper fake with deterministic token counts."""

    def __init__(self) -> None:
        self.calls = 0

    def send(self, provider: str, messages: list[dict[str, str]]) -> ProviderResponse:
        """Return larger token use for raw-code calls than guided calls."""
        self.calls += 1
        content = messages[0]["content"]
        input_tokens = 100 if "---" in content else 30
        return ProviderResponse(
            text=json.dumps({
                "root_cause": "root cause found",
                "suspected_files": ["app.py"],
                "suspected_symbols": ["bug"],
                "confidence": "high",
                "evidence": [{
                    "file": "app.py", "line_start": 1, "line_end": 1,
                    "symbol": "bug", "reason": "test fixture",
                }],
            }),
            input_tokens=input_tokens,
            output_tokens=10,
            provider=provider,
            model="fake",
        )

    def get_call_log(self) -> list[dict]:
        """Return empty logs; unused by tests."""
        return []

    def get_queue_status(self) -> dict:
        """Return idle status; unused by tests."""
        return {"queue_size": 0}


def test_comparison_service_runs_both_modes(tmp_path: Path) -> None:
    """ComparisonService returns metrics and narrative."""
    source = tmp_path / "app.py"
    source.write_text("def bug(): pass\n", encoding="utf-8")
    vault = tmp_path / "vault"
    vault.mkdir()
    (vault / "index.md").write_text("# Index", encoding="utf-8")
    graph = GraphData(entities=[Entity("bug", "function", "app.py", (1, 1))])
    gatekeeper = FakeGatekeeper()

    report = ComparisonService(gatekeeper, "fake").run_comparison("bug", [source], graph, vault)

    assert gatekeeper.calls == 2
    assert report.metrics.naive.files_read == 1
    assert report.metrics.guided.files_read == 1
    assert report.metrics.token_savings_pct > 0
    assert "| Tokens |" in report.narrative


def test_canonical_comparison_uses_distinct_fair_requests(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.chdir(tmp_path)
    source = tmp_path / "app.py"
    source.write_text("def bug(): pass\n", encoding="utf-8")
    graph = GraphData(entities=[Entity("bug", "function", "app.py", (1, 1))])
    req = ComparisonRequest(
        bug_report="bug", provider="fake", run_id="cmp", target_snapshot_path=str(tmp_path)
    )
    service = ComparisonService(FakeGatekeeper(), "fake")

    outcome = service.run_comparison(req, [source], graph, None)

    assert isinstance(outcome, ComparisonOutcome)
    assert outcome.naive_result.run_id == "cmp-naive"
    assert outcome.guided_result.run_id == "cmp-graph"
    assert outcome.naive_result.config_hash == req.controlled_config_hash()
    assert outcome.guided_result.config_hash == req.controlled_config_hash()


def test_canonical_comparison_persists_missing_graph_diff_without_losing_metrics(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.chdir(tmp_path)
    source = tmp_path / "app.py"
    source.write_text("def bug(): pass\n", encoding="utf-8")
    graph = GraphData(entities=[Entity("bug", "function", "app.py", (1, 1))])
    req = ComparisonRequest(
        bug_report="bug",
        provider="fake",
        run_id="cmp",
        target_snapshot_path=str(tmp_path),
        artifact_root="artifacts",
    )
    service = ComparisonService(FakeGatekeeper(), "fake")

    service.run_comparison(req, [source], graph, None)

    graph_diff = tmp_path / "artifacts" / "runs" / "cmp" / "reports" / "graph_diff.json"
    comparison = tmp_path / "artifacts" / "runs" / "cmp" / "reports" / "comparison.json"
    manifest = tmp_path / "artifacts" / "manifests" / "cmp-naive_manifest.json"
    assert graph_diff.exists()
    assert comparison.exists()
    assert json.loads(graph_diff.read_text(encoding="utf-8"))["status"] == "missing"
    assert json.loads(comparison.read_text(encoding="utf-8"))["signed_metrics"]["naive_tokens"] == 110
    assert json.loads(manifest.read_text(encoding="utf-8"))["graph_diff_hash"]


def test_canonical_comparison_accepts_real_post_graph(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.chdir(tmp_path)
    source = tmp_path / "app.py"
    source.write_text("def bug(): pass\n", encoding="utf-8")
    pre_graph = GraphData(entities=[Entity("bug", "function", "app.py", (1, 1))])
    post_graph = GraphData(
        entities=[
            Entity("bug", "function", "app.py", (1, 1)),
            Entity("fix", "function", "app.py", (2, 2)),
        ],
        relationships=[Relationship("fix", "bug", "calls", key="fix->bug")],
    )
    req = ComparisonRequest(
        bug_report="bug",
        provider="fake",
        run_id="cmp",
        target_snapshot_path=str(tmp_path),
        artifact_root="artifacts",
    )

    ComparisonService(FakeGatekeeper(), "fake").run_comparison(
        req,
        [source],
        pre_graph,
        None,
        post_graph=post_graph,
    )

    graph_diff = tmp_path / "artifacts" / "runs" / "cmp" / "reports" / "graph_diff.json"
    data = json.loads(graph_diff.read_text(encoding="utf-8"))
    assert data["status"] == "available"
    assert data["post_snapshot"]["entity_count"] == 2


def test_fairness_failure_occurs_before_provider_calls(tmp_path: Path) -> None:
    class RejectingEnforcer:
        def check(self, naive: ComparisonRequest, guided: ComparisonRequest) -> None:
            assert naive is not guided
            raise FairnessViolationError("stop")

    gatekeeper = FakeGatekeeper()
    service = ComparisonService(gatekeeper, "fake")
    service._enforcer = RejectingEnforcer()  # regression test for pre-call ordering
    req = ComparisonRequest(bug_report="bug", provider="fake", run_id="cmp")

    with pytest.raises(FairnessViolationError):
        service.run_comparison(req, [], None, None)
    assert gatekeeper.calls == 0
