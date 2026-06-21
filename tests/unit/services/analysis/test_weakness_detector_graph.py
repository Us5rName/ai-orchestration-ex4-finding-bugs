import pytest

from ex04.services.analysis.weakness_detector import (
    DependencyPathRequirement,
    EvidenceConfidence,
    WeaknessConfig,
    WeaknessDetector,
    WeaknessSignal,
)
from ex04.shared.types import Entity, GraphData, Relationship


def graph(
    entities: list[Entity],
    relationships: list[Relationship] | None = None,
) -> GraphData:
    return GraphData(entities=entities, relationships=relationships or [])


def test_high_degree_handles_ties_self_loops_and_parallel_edges() -> None:
    data = graph(
        [Entity("a", label="A"), Entity("b", label="A"), Entity("c")],
        [
            Relationship("a", "b", "calls", key="1"),
            Relationship("a", "b", "calls", key="2"),
            Relationship("a", "a", "calls", key="3"),
            Relationship("c", "a", "calls", key="4"),
        ],
    )
    report = WeaknessDetector(WeaknessConfig(degree_threshold=2)).detect(data)
    findings = [f for f in report.findings if f.signal is WeaknessSignal.HIGH_DEGREE]
    assert [f.entity_ids for f in findings] == [("a",), ("b",)]
    assert [f.finding_id for f in findings] == [
        f.finding_id for f in WeaknessDetector(WeaknessConfig(degree_threshold=2)).detect(data).findings
        if f.signal is WeaknessSignal.HIGH_DEGREE
    ]


def test_isolated_component_reuses_component_semantics() -> None:
    data = graph(
        [Entity("a"), Entity("b"), Entity("c"), Entity("d")],
        [Relationship("a", "b", "calls")],
    )
    report = WeaknessDetector(WeaknessConfig(weak_component_max_size=2)).detect(data)
    components = [f for f in report.findings if f.signal is WeaknessSignal.ISOLATED_COMPONENT]
    assert sorted(item.entity_ids for item in components) == [("a", "b"), ("c",), ("d",)]
    assert all("Low connectivity is not proof" in item.limitations[0] for item in components)


@pytest.mark.parametrize(
    ("relationship", "expected_confidence"),
    [
        (Relationship("a", "b", "calls", confidence="ambiguous"), EvidenceConfidence.AMBIGUOUS),
        (Relationship("a", "b", "calls", confidence="inferred"), EvidenceConfidence.INFERRED),
        (Relationship("a", "b", "calls"), EvidenceConfidence.UNKNOWN),
        (
            Relationship("a", "b", "calls", confidence="extracted", confidence_score=0.2),
            EvidenceConfidence.EXTRACTED,
        ),
    ],
)
def test_relationship_confidence_states_emit_distinct_findings(
    relationship: Relationship, expected_confidence: EvidenceConfidence
) -> None:
    report = WeaknessDetector(WeaknessConfig(confidence_threshold=0.5)).detect(
        graph([Entity("a"), Entity("b")], [relationship])
    )
    findings = [f for f in report.findings if f.signal is WeaknessSignal.RELATIONSHIP_CONFIDENCE]
    assert findings
    assert findings[0].confidence is expected_confidence


def test_extracted_high_confidence_relationship_is_not_reported() -> None:
    data = graph(
        [Entity("a"), Entity("b")],
        [Relationship("a", "b", "calls", confidence="extracted", confidence_score=0.9)],
    )
    report = WeaknessDetector(WeaknessConfig(confidence_threshold=0.5)).detect(data)
    assert not [f for f in report.findings if f.signal is WeaknessSignal.RELATIONSHIP_CONFIDENCE]


def test_broken_dependency_path_respects_direction_type_and_depth() -> None:
    data = graph(
        [Entity("a"), Entity("b"), Entity("c")],
        [Relationship("a", "b", "calls"), Relationship("b", "c", "imports")],
    )
    config = WeaknessConfig(
        expected_paths=(DependencyPathRequirement("a", "c", ("calls",), 2),)
    )
    report = WeaknessDetector(config).detect(data)
    findings = [f for f in report.findings if f.signal is WeaknessSignal.BROKEN_DEPENDENCY_PATH]
    assert findings[0].entity_ids == ("a", "c")


def test_unknown_dependency_endpoint_is_configuration_error() -> None:
    data = graph([Entity("a")])
    config = WeaknessConfig(expected_paths=(DependencyPathRequirement("a", "missing", (), None),))
    with pytest.raises(ValueError, match="unknown dependency path endpoint"):
        WeaknessDetector(config).detect(data)
