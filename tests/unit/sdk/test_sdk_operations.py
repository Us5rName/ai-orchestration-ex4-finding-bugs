"""Tests for new ComparisonOpsMixin SDK operations.

Traceability: [TODO P6-R07]
"""

from __future__ import annotations

import json
from pathlib import Path
from unittest.mock import MagicMock

from ex04.sdk._comparison_ops import _to_run_metrics
from ex04.shared.types_experiment import RunManifest, SignedMetrics
from ex04.shared.types_request import ComparisonRequest
from ex04.shared.types_results import InvestigationResult


def _fake_sdk(tmp_path: Path) -> object:
    """Build a minimal SDK-like object with mocked services."""
    from ex04.sdk.sdk import Ex04SDK
    from ex04.services.comparison.service import ComparisonService
    from ex04.shared.gatekeeper import GatekeeperInterface

    gk = MagicMock(spec=GatekeeperInterface)
    gk.send.return_value = MagicMock(
        text='{"root_cause": "x", "suspected_files": [], "suspected_symbols": []}',
        input_tokens=10, output_tokens=20,
    )
    cmp = ComparisonService(gk, "openai")

    sdk = Ex04SDK.__new__(Ex04SDK)
    sdk._comparison = cmp
    sdk._config = {"artifact_root": str(tmp_path / "artifacts"), "paths": {}}
    return sdk


def test_to_run_metrics_found_root_cause() -> None:
    """_to_run_metrics maps parsed_ok + pass_without_gate to found_root_cause=True."""
    r = InvestigationResult(
        parser_status="parsed_ok", gate_status="pass_without_gate",
        input_tokens=100, output_tokens=200, files_read=3, iterations=1,
        duration_seconds=0.5,
    )
    rm = _to_run_metrics(r)
    assert rm.found_root_cause is True
    assert rm.tokens_used == 300
    assert rm.files_read == 3


def test_to_run_metrics_failed_parse() -> None:
    """_to_run_metrics maps parse_failed to found_root_cause=False."""
    r = InvestigationResult(parser_status="parse_failed", gate_status="pass_without_gate")
    assert _to_run_metrics(r).found_root_cause is False


def test_run_naive_investigation_returns_result(tmp_path: Path) -> None:
    """run_naive_investigation returns InvestigationResult with run_id populated."""
    sdk = _fake_sdk(tmp_path)
    req = ComparisonRequest(bug_report="test bug", provider="openai", run_id="r001")
    result = sdk.run_naive_investigation(req, source_files=[])
    assert isinstance(result, InvestigationResult)
    assert result.run_id == "r001"
    assert result.mode == "naive"


def test_run_graph_investigation_returns_result(tmp_path: Path) -> None:
    """run_graph_investigation returns InvestigationResult with mode=graph."""
    sdk = _fake_sdk(tmp_path)
    req = ComparisonRequest(bug_report="test bug", provider="openai", run_id="r002")
    result = sdk.run_graph_investigation(req)
    assert isinstance(result, InvestigationResult)
    assert result.mode == "graph"


def test_run_experiment_returns_triple(tmp_path: Path) -> None:
    """run_experiment returns (naive, guided, SignedMetrics)."""
    sdk = _fake_sdk(tmp_path)
    req = ComparisonRequest(bug_report="test bug", provider="openai", run_id="r003")
    naive, guided, metrics = sdk.run_experiment(req)
    assert isinstance(naive, InvestigationResult)
    assert isinstance(guided, InvestigationResult)
    assert isinstance(metrics, SignedMetrics)


def test_compute_metrics_returns_signed_metrics(tmp_path: Path) -> None:
    """compute_metrics delegates to SignedMetricsCalculator."""
    sdk = _fake_sdk(tmp_path)
    naive = InvestigationResult(parser_status="parsed_ok", gate_status="pass_without_gate",
                                input_tokens=300, output_tokens=100, files_read=5)
    guided = InvestigationResult(parser_status="parsed_ok", gate_status="pass_without_gate",
                                 input_tokens=100, output_tokens=50, files_read=2)
    metrics = sdk.compute_metrics(naive, guided)
    assert isinstance(metrics, SignedMetrics)
    assert metrics.naive_tokens == 400
    assert metrics.guided_tokens == 150


def test_save_manifest_creates_file(tmp_path: Path) -> None:
    """save_manifest writes a manifest JSON and returns its path."""
    sdk = _fake_sdk(tmp_path)
    manifest = RunManifest(run_id="save-test-001", mode="naive", evidence_class="fixture")
    path = sdk.save_manifest(manifest)
    assert path.exists()
    data = json.loads(path.read_text())
    assert data["run_id"] == "save-test-001"


def test_load_provenance_reads_json(tmp_path: Path) -> None:
    """load_provenance reads and returns provenance.json contents."""
    prov_dir = tmp_path / "artifacts" / "pre_fix"
    prov_dir.mkdir(parents=True)
    prov_file = prov_dir / "provenance.json"
    prov_file.write_text(json.dumps({"target_repo": "andela/buggy-python"}))

    sdk = _fake_sdk(tmp_path)
    data = sdk.load_provenance(str(prov_file))
    assert data["target_repo"] == "andela/buggy-python"
