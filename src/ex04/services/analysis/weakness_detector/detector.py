"""WeaknessDetector orchestration."""

from __future__ import annotations

from pathlib import Path
from typing import Protocol

from ex04.services.analysis.weakness_detector.config import WeaknessConfig
from ex04.services.analysis.weakness_detector.models import (
    SignalStatus,
    ValidationStatus,
    WeaknessFinding,
    WeaknessReport,
    WeaknessSignal,
)
from ex04.services.analysis.weakness_detector.ranking import coalesce_findings, rank_findings
from ex04.services.analysis.weakness_detector.signals_graph import (
    high_degree_signal,
    isolated_component_signal,
    relationship_confidence_signal,
)
from ex04.services.analysis.weakness_detector.signals_paths import broken_path_signal
from ex04.services.analysis.weakness_detector.signals_source import semantic_duplicate_signal
from ex04.services.analysis.weakness_detector.source_index import SourceIndex
from ex04.services.analysis.weakness_detector.utils import graph_hash
from ex04.services.graph.interface import GraphReaderInterface, build_graph_reader
from ex04.shared.types import GraphData

DETECTOR_VERSION = "1.0"


class WeaknessSignalDetector(Protocol):
    """Narrow signal detector protocol."""

    signal: WeaknessSignal

    def detect(
        self, *, reader: GraphReaderInterface, source_index: SourceIndex, config: WeaknessConfig
    ) -> tuple[WeaknessFinding, ...]:
        """Run one signal."""


class WeaknessDetector:
    """Detect generic graph/source weaknesses without provider calls."""

    def __init__(
        self,
        config: WeaknessConfig | None = None,
        source_root: Path | None = None,
    ) -> None:
        self._config = config or WeaknessConfig()
        self._source_root = source_root

    def detect(self, graph_data: GraphData) -> WeaknessReport:
        """Run all configured signals and return an immutable report."""
        reader = build_graph_reader(graph_data)
        source_index = SourceIndex(self._source_root, self._config.source_max_bytes)
        all_findings: list[WeaknessFinding] = []
        statuses: list[SignalStatus] = []
        for signal, func in _SIGNALS:
            try:
                findings = func(reader=reader, source_index=source_index, config=self._config)
                all_findings.extend(findings)
                statuses.append(SignalStatus(signal, ValidationStatus.VALID, "ok"))
            except ValueError as exc:
                statuses.append(SignalStatus(signal, ValidationStatus.ERROR, str(exc)))
                raise
        ranked = rank_findings(coalesce_findings(tuple(all_findings)), self._config)
        return WeaknessReport(
            findings=ranked,
            detector_version=DETECTOR_VERSION,
            config_hash=self._config.config_hash,
            graph_snapshot_hash=graph_hash(reader),
            limitations=("Findings are static analysis signals, not proof of defects.",),
            signal_statuses=tuple(statuses),
        )


_SIGNALS = (
    (WeaknessSignal.HIGH_DEGREE, high_degree_signal),
    (WeaknessSignal.ISOLATED_COMPONENT, isolated_component_signal),
    (WeaknessSignal.RELATIONSHIP_CONFIDENCE, relationship_confidence_signal),
    (WeaknessSignal.BROKEN_DEPENDENCY_PATH, broken_path_signal),
    (WeaknessSignal.SEMANTIC_DUPLICATE, semantic_duplicate_signal),
)
