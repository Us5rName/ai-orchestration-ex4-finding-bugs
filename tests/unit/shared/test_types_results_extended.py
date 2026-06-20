"""Tests for extended InvestigationResult and StructuredEvidence types.

Traceability: [TODO P6-R02-REV]
"""

from __future__ import annotations

from ex04.shared.types_evidence import StructuredEvidence
from ex04.shared.types_results import InvestigationResult


def test_structured_evidence_defaults() -> None:
    ev = StructuredEvidence()
    assert ev.source_file == ""
    assert ev.sent_to_model is False
    assert ev.in_final_diagnosis is False
    assert ev.ranking_score == 0.0
    assert ev.dependency_path == ""


def test_structured_evidence_with_values() -> None:
    ev = StructuredEvidence(
        source_file="buggy.py",
        line_start=10,
        line_end=20,
        graph_node="process_data",
        sent_to_model=True,
        ranking_score=0.9,
    )
    assert ev.source_file == "buggy.py"
    assert ev.graph_node == "process_data"
    assert ev.sent_to_model is True
    assert ev.in_final_diagnosis is False


def test_investigation_result_new_fields_defaults() -> None:
    res = InvestigationResult()
    assert res.run_id == ""
    assert res.mode == ""
    assert res.config_hash == ""
    assert res.target_commit == "unknown"
    assert res.parser_status == "not_run"
    assert res.diagnosis_status == "unverified"
    assert res.gate_status == "not_requested"
    assert res.verification_status == "unverified"
    assert res.telemetry_available is False
    assert res.input_tokens is None
    assert res.output_tokens is None
    assert res.context_tokens == 0
    assert res.bytes_read == 0
    assert res.tool_calls == 0
    assert res.model_calls == 0
    assert res.iterations == 0
    assert res.retries == 0
    assert res.duration_seconds == 0.0
    assert res.estimated_cost_usd is None
    assert res.evidence_class == "fixture"
    assert res.trace_path == ""
    assert res.trace_hash == ""


def test_investigation_result_evidence_list() -> None:
    ev = StructuredEvidence(source_file="buggy.py", ranking_score=0.8, sent_to_model=True)
    res = InvestigationResult(run_id="r1", mode="naive", evidence=[ev])
    assert len(res.evidence) == 1
    assert res.evidence[0].source_file == "buggy.py"
    assert res.evidence[0].sent_to_model is True


def test_investigation_result_limitations_list() -> None:
    res = InvestigationResult(limitations=["anchor missing", "telemetry blocked"])
    assert len(res.limitations) == 2
    assert "telemetry blocked" in res.limitations


def test_investigation_result_existing_fields_intact() -> None:
    """Ensure original InvestigationResult fields are unchanged."""
    res = InvestigationResult(
        root_cause="off-by-one",
        files_read=3,
        fix_applied=True,
    )
    assert res.root_cause == "off-by-one"
    assert res.files_read == 3
    assert res.fix_applied is True
    assert res.suspects == []
    assert res.test_results == {}
