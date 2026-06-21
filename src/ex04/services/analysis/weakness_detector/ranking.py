"""Deterministic coalescing and ranking for weakness findings."""

from __future__ import annotations

from dataclasses import replace

from ex04.services.analysis.weakness_detector.config import WeaknessConfig
from ex04.services.analysis.weakness_detector.models import Severity, WeaknessFinding

_SEVERITY_ORDER = {
    Severity.INFO: 0,
    Severity.LOW: 1,
    Severity.MEDIUM: 2,
    Severity.HIGH: 3,
    Severity.CRITICAL: 4,
}


def coalesce_findings(findings: tuple[WeaknessFinding, ...]) -> tuple[WeaknessFinding, ...]:
    """Deduplicate by stable finding_id preserving evidence and strongest severity."""
    grouped: dict[str, WeaknessFinding] = {}
    for item in findings:
        existing = grouped.get(item.finding_id)
        if existing is None:
            grouped[item.finding_id] = item
            continue
        grouped[item.finding_id] = replace(
            item if _SEVERITY_ORDER[item.severity] >= _SEVERITY_ORDER[existing.severity] else existing,
            evidence=tuple(sorted(set(existing.evidence + item.evidence), key=str)),
            limitations=tuple(sorted(set(existing.limitations + item.limitations))),
        )
    return tuple(grouped.values())


def rank_findings(
    findings: tuple[WeaknessFinding, ...],
    config: WeaknessConfig,
) -> tuple[WeaknessFinding, ...]:
    """Rank findings by score/severity with stable secondary keys."""
    ranked = sorted(
        findings,
        key=lambda f: (-f.score, -_SEVERITY_ORDER[f.severity], f.signal.value, f.finding_id),
    )
    return tuple(ranked[:config.max_total_findings])
