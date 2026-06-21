from dataclasses import FrozenInstanceError

import pytest

from ex04.services.analysis.weakness_detector import (
    DependencyPathRequirement,
    EvidenceConfidence,
    Severity,
    WeaknessConfig,
    WeaknessFinding,
    WeaknessSignal,
)


def test_config_rejects_invalid_thresholds_and_weights() -> None:
    with pytest.raises(ValueError, match="degree_threshold"):
        WeaknessConfig(degree_threshold=-1)
    with pytest.raises(ValueError, match="confidence_threshold"):
        WeaknessConfig(confidence_threshold=1.5)
    with pytest.raises(ValueError, match="ranking_weights"):
        WeaknessConfig(ranking_weights=(1.0, float("nan"), 0.1))
    with pytest.raises(ValueError, match="severity_boundaries"):
        WeaknessConfig(severity_boundaries=(0.3, 0.2, 0.8, 0.9))


def test_path_requirements_are_validated() -> None:
    requirement = DependencyPathRequirement("a", "b", ("calls",), 2)
    assert requirement.allowed_relationship_types == ("calls",)
    with pytest.raises(ValueError, match="max_depth"):
        DependencyPathRequirement("a", "b", ("calls",), -1)
    with pytest.raises(ValueError, match="source_id"):
        DependencyPathRequirement("", "b", ("calls",), None)


def test_public_models_are_immutable_and_serializable() -> None:
    finding = WeaknessFinding(
        finding_id="x",
        signal=WeaknessSignal.HIGH_DEGREE,
        tag="degree",
        severity=Severity.LOW,
        confidence=EvidenceConfidence.EXTRACTED,
        score=0.3,
        summary="measured degree",
        entity_ids=("a",),
    )
    with pytest.raises(FrozenInstanceError):
        finding.score = 0.9  # type: ignore[misc]
    assert finding.to_dict()["signal"] == "high_degree"
    assert finding.to_dict()["entity_ids"] == ["a"]
