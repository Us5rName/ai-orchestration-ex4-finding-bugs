"""Phase 7 comparison regression tests."""

import json
from pathlib import Path

from ex04.phase7 import run_phase7_comparison

TARGET = Path("graph-home/.graphify/repos/andela/buggy-python")
GRAPH = Path("graph-home/graphify-out/graph.json")
VAULT = Path("obsidian")


def test_phase7_comparison_runner_persists_report(
    tmp_path: Path,
    monkeypatch,
) -> None:
    """Phase 7 comparison uses the canonical service and persists reports."""
    target = TARGET.resolve()
    graph = GRAPH.resolve()
    vault = VAULT.resolve()
    monkeypatch.chdir(tmp_path)

    outcome = run_phase7_comparison(
        target_path=target,
        graph_path=graph,
        vault_path=vault,
        artifact_root=Path("artifacts"),
    )

    assert outcome.signed_metrics.token_savings_pct is not None
    assert outcome.signed_metrics.token_savings_pct >= 30
    assert all(Path(path).is_file() for path in outcome.report_paths)


def test_phase7_comparison_artifacts_are_committed() -> None:
    """Committed Phase 7 comparison artifacts must include metrics and reports."""
    report = Path("artifacts/runs/phase7-comparison/reports/comparison.md")
    data = json.loads(
        Path("artifacts/runs/phase7-comparison/reports/comparison.json").read_text(
            encoding="utf-8"
        )
    )

    assert report.is_file()
    assert "| Tokens |" in report.read_text(encoding="utf-8")
    assert data["signed_metrics"]["token_savings_pct"] >= 30
    assert Path("artifacts/manifests/phase7-comparison-naive_manifest.json").is_file()
    assert Path("artifacts/manifests/phase7-comparison-graph_manifest.json").is_file()
