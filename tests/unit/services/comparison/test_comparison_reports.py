"""Tests for write_comparison_reports (JSON + Markdown outputs).

Traceability: [TODO P7-R04]
"""

from __future__ import annotations

import json
from pathlib import Path

from ex04.services.comparison.report_gen import write_comparison_reports
from ex04.shared.types_experiment import SignedMetrics
from ex04.shared.types_results import InvestigationResult


def _make_result(mode: str, run_id: str = "r001") -> InvestigationResult:
    return InvestigationResult(
        root_cause="off-by-one",
        original_problem="crash",
        files_read=3,
        parser_status="parsed_ok",
        gate_status="pass_without_gate",
        evidence_class="fixture",
        limitations=["telemetry_blocked"],
        run_id=run_id,
        mode=mode,
    )


def _make_metrics() -> SignedMetrics:
    return SignedMetrics(
        naive_tokens=400, guided_tokens=150,
        token_delta=250, token_savings_pct=62.5,
        naive_files=5, guided_files=2, file_delta=3,
        naive_iterations=2, guided_iterations=1, iteration_delta=1,
        naive_duration=1.2, guided_duration=0.4, duration_delta=0.8,
        naive_correct=True, guided_correct=True,
    )


def test_json_report_written(tmp_path: Path) -> None:
    """write_comparison_reports creates comparison.json."""
    naive = _make_result("naive")
    guided = _make_result("graph", run_id="r002")
    metrics = _make_metrics()
    json_path, _ = write_comparison_reports(naive, guided, metrics, tmp_path)
    assert json_path.exists()


def test_json_report_fields(tmp_path: Path) -> None:
    """comparison.json contains required top-level fields."""
    naive = _make_result("naive")
    guided = _make_result("graph", run_id="r002")
    metrics = _make_metrics()
    json_path, _ = write_comparison_reports(naive, guided, metrics, tmp_path)
    data = json.loads(json_path.read_text())
    for key in ("evidence_class", "naive_run_id", "guided_run_id",
                 "signed_metrics", "naive_limitations", "guided_limitations"):
        assert key in data, f"Missing key: {key}"


def test_markdown_report_has_evidence_banner(tmp_path: Path) -> None:
    """comparison.md includes an evidence class banner."""
    naive = _make_result("naive")
    guided = _make_result("graph", run_id="r002")
    metrics = _make_metrics()
    _, md_path = write_comparison_reports(naive, guided, metrics, tmp_path)
    text = md_path.read_text()
    assert "Evidence Class" in text
    assert "FIXTURE" in text


def test_markdown_report_has_sha256(tmp_path: Path) -> None:
    """comparison.md includes a SHA-256 hash prefix of the JSON report."""
    naive = _make_result("naive")
    guided = _make_result("graph", run_id="r002")
    metrics = _make_metrics()
    _, md_path = write_comparison_reports(naive, guided, metrics, tmp_path)
    assert "SHA-256" in md_path.read_text()
