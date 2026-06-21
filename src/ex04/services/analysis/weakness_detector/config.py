"""Validated configuration for weakness detection."""

from __future__ import annotations

import hashlib
import json
import math
from dataclasses import asdict, dataclass
from typing import cast


@dataclass(frozen=True, slots=True)
class DependencyPathRequirement:
    """Expected directed dependency path."""

    source_id: str
    target_id: str
    allowed_relationship_types: tuple[str, ...] = ()
    max_depth: int | None = None

    def __post_init__(self) -> None:
        """Validate a directed reachability expectation."""
        if not self.source_id or not self.target_id:
            raise ValueError("source_id and target_id are required")
        if self.max_depth is not None and self.max_depth < 0:
            raise ValueError("max_depth must be non-negative")


@dataclass(frozen=True, slots=True)
class WeaknessConfig:
    """Validated detector configuration."""

    degree_threshold: int = 3
    max_high_degree_findings: int = 5
    weak_component_max_size: int = 2
    confidence_threshold: float = 0.5
    include_missing_confidence: bool = True
    expected_paths: tuple[DependencyPathRequirement, ...] = ()
    duplicate_strategy: str = "normalized_ast"
    severity_boundaries: tuple[float, float, float, float] = (0.25, 0.5, 0.75, 0.9)
    ranking_weights: tuple[float, float, float] = (0.5, 0.25, 0.25)
    max_total_findings: int = 50
    source_max_bytes: int = 262_144

    def __post_init__(self) -> None:
        """Validate all configuration values."""
        if self.degree_threshold < 0 or self.max_high_degree_findings < 0:
            raise ValueError("degree_threshold and max_high_degree_findings must be non-negative")
        if self.weak_component_max_size < 1:
            raise ValueError("weak_component_max_size must be positive")
        if not 0.0 <= self.confidence_threshold <= 1.0:
            raise ValueError("confidence_threshold must be in [0, 1]")
        if self.duplicate_strategy not in {"normalized_ast", "disabled"}:
            raise ValueError(f"unsupported duplicate strategy: {self.duplicate_strategy}")
        if sorted(self.severity_boundaries) != list(self.severity_boundaries):
            raise ValueError("severity_boundaries must be ascending")
        if any(not 0.0 <= b <= 1.0 for b in self.severity_boundaries):
            raise ValueError("severity_boundaries must be in [0, 1]")
        if any((not math.isfinite(w)) or w < 0 for w in self.ranking_weights):
            raise ValueError("ranking_weights must be finite and non-negative")
        if sum(self.ranking_weights) <= 0:
            raise ValueError("at least one ranking weight must be positive")
        if self.max_total_findings < 0 or self.source_max_bytes < 0:
            raise ValueError("max_total_findings and source_max_bytes must be non-negative")
        for req in self.expected_paths:
            if req.max_depth is not None and req.max_depth < 0:
                raise ValueError("dependency path max_depth must be non-negative")

    @property
    def config_hash(self) -> str:
        """Stable SHA-256 of normalized configuration."""
        payload = json.dumps(asdict(self), sort_keys=True, default=str)
        return hashlib.sha256(payload.encode("utf-8")).hexdigest()


def config_from_dict(data: dict[str, object] | None = None) -> WeaknessConfig:
    """Build config from a plain dict."""
    if not data:
        return WeaknessConfig()
    path_data = cast(tuple[dict[str, object], ...], data.get("expected_paths", ()))
    paths = tuple(
        DependencyPathRequirement(
            source_id=str(item["source_id"]),
            target_id=str(item["target_id"]),
            allowed_relationship_types=tuple(cast(tuple[str, ...], item.get("allowed_relationship_types", ()))),
            max_depth=cast(int | None, item.get("max_depth")),
        )
        for item in path_data
    )
    values = {k: v for k, v in data.items() if k != "expected_paths"}
    return WeaknessConfig(expected_paths=paths, **values)  # type: ignore[arg-type]
