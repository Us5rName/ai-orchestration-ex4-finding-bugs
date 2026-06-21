"""Immutable public models for weakness detection."""

from __future__ import annotations

from dataclasses import asdict, dataclass
from enum import StrEnum
from typing import Any


class WeaknessSignal(StrEnum):
    """Supported weakness signal types."""

    HIGH_DEGREE = "high_degree"
    ISOLATED_COMPONENT = "isolated_component"
    RELATIONSHIP_CONFIDENCE = "relationship_confidence"
    BROKEN_DEPENDENCY_PATH = "broken_dependency_path"
    SEMANTIC_DUPLICATE = "semantic_duplicate"


class Severity(StrEnum):
    """Finding severity levels."""

    INFO = "info"
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class EvidenceConfidence(StrEnum):
    """Evidence confidence source labels."""

    EXTRACTED = "extracted"
    INFERRED = "inferred"
    AMBIGUOUS = "ambiguous"
    UNKNOWN = "unknown"


class ValidationStatus(StrEnum):
    """Source validation outcome."""

    VALID = "valid"
    MISSING = "missing"
    SYNTAX_ERROR = "syntax_error"
    NOT_CHECKED = "not_checked"
    ERROR = "error"


@dataclass(frozen=True, slots=True)
class EvidenceAnchor:
    """Typed source location evidence."""

    file_path: str
    start_line: int | None = None
    end_line: int | None = None
    entity_id: str | None = None


@dataclass(frozen=True, slots=True)
class RelationshipKey:
    """Stable relationship reference."""

    source_id: str
    target_id: str
    relationship_type: str
    parallel_key: str | None = None


@dataclass(frozen=True, slots=True)
class ScoreComponents:
    """Explainable score components in normalized range."""

    structural: float
    evidence: float
    confidence: float


@dataclass(frozen=True, slots=True)
class SourceValidation:
    """Bounded source-read validation details."""

    status: ValidationStatus
    detail: str = ""


@dataclass(frozen=True, slots=True)
class WeaknessFinding:
    """One deterministic weakness finding."""

    finding_id: str
    signal: WeaknessSignal
    tag: str
    severity: Severity
    confidence: EvidenceConfidence
    score: float
    summary: str
    entity_ids: tuple[str, ...] = ()
    relationship_keys: tuple[RelationshipKey, ...] = ()
    evidence: tuple[EvidenceAnchor, ...] = ()
    source_validation: SourceValidation = SourceValidation(ValidationStatus.NOT_CHECKED)
    score_components: ScoreComponents = ScoreComponents(0.0, 0.0, 0.0)
    limitations: tuple[str, ...] = ()

    def to_dict(self) -> dict[str, Any]:
        """Return stable JSON-compatible data."""
        return _normalize(asdict(self))


@dataclass(frozen=True, slots=True)
class SignalStatus:
    """Execution status for one signal detector."""

    signal: WeaknessSignal
    status: ValidationStatus
    detail: str = ""


@dataclass(frozen=True, slots=True)
class WeaknessReport:
    """Aggregate deterministic weakness report."""

    findings: tuple[WeaknessFinding, ...]
    detector_version: str
    config_hash: str
    graph_snapshot_hash: str
    limitations: tuple[str, ...]
    signal_statuses: tuple[SignalStatus, ...]

    def to_dict(self) -> dict[str, Any]:
        """Return stable JSON-compatible data."""
        return _normalize(asdict(self))


def _normalize(value: Any) -> Any:
    if isinstance(value, StrEnum):
        return value.value
    if isinstance(value, dict):
        return {str(k): _normalize(v) for k, v in sorted(value.items())}
    if isinstance(value, list | tuple):
        return [_normalize(v) for v in value]
    return value
