"""Multi-signal weakness detector package."""

from ex04.services.analysis.weakness_detector.config import (
    DependencyPathRequirement,
    WeaknessConfig,
    config_from_dict,
)
from ex04.services.analysis.weakness_detector.detector import WeaknessDetector
from ex04.services.analysis.weakness_detector.models import (
    EvidenceAnchor,
    EvidenceConfidence,
    RelationshipKey,
    ScoreComponents,
    Severity,
    SourceValidation,
    ValidationStatus,
    WeaknessFinding,
    WeaknessReport,
    WeaknessSignal,
)

__all__ = [
    "DependencyPathRequirement",
    "EvidenceAnchor",
    "EvidenceConfidence",
    "RelationshipKey",
    "ScoreComponents",
    "Severity",
    "SourceValidation",
    "ValidationStatus",
    "WeaknessConfig",
    "WeaknessDetector",
    "WeaknessFinding",
    "WeaknessReport",
    "WeaknessSignal",
    "config_from_dict",
]
