"""Tests for StructuredEvidence and InvestigationRunRecord types."""

from __future__ import annotations

from ex04.shared.types_investigation import InvestigationRunRecord, StructuredEvidence


def test_structured_evidence_defaults() -> None:
    ev = StructuredEvidence()
    assert ev.source_file == ""
    assert ev.sent_to_model is False
    assert ev.in_final_diagnosis is False
    assert ev.ranking_score == 0.0


def test_structured_evidence_with_values() -> None:
    ev = StructuredEvidence(
        source_file="buggy.py",
        line_start=10,
        line_end=20,
        graph_node="process_data",
        sent_to_model=True,
    )
    assert ev.source_file == "buggy.py"
    assert ev.graph_node == "process_data"
    assert ev.sent_to_model is True


def test_run_record_defaults() -> None:
    rec = InvestigationRunRecord()
    assert rec.run_id == ""
    assert rec.telemetry_available is False
    assert rec.input_tokens is None
    assert rec.evidence == []
    assert rec.trace == []


def test_run_record_with_evidence() -> None:
    ev = StructuredEvidence(source_file="buggy.py", ranking_score=0.9)
    rec = InvestigationRunRecord(
        run_id="r1",
        mode="naive",
        evidence=[ev],
        telemetry_available=False,
    )
    assert len(rec.evidence) == 1
    assert rec.evidence[0].source_file == "buggy.py"
    assert rec.evidence_class == "fixture"
