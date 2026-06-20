"""Tests for AnalysisService facade."""

from ex04.services.analysis.service import AnalysisService
from ex04.shared.types import Entity, GraphData, InvestigationResult


def test_analysis_service_reverse_engineer_and_report() -> None:
    service = AnalysisService()
    graph = GraphData(entities=[Entity("OrderService", "class", "order.py")])
    investigation = InvestigationResult(root_cause="missing validation")

    architecture = service.reverse_engineer(graph)
    report = service.report(investigation)

    assert "Architecture Analysis" in architecture
    assert "missing validation" in report
