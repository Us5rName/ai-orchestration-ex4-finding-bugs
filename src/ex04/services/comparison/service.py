"""Comparison service facade for naive vs. graph-guided runs."""

from __future__ import annotations

from pathlib import Path

from ex04.services.comparison.fairness import FairnessEnforcer
from ex04.services.comparison.graph_guided_runner import GraphGuidedRunner
from ex04.services.comparison.interface import ComparisonServiceInterface
from ex04.services.comparison.metrics import MetricsCalculator
from ex04.services.comparison.naive_runner import NaiveRunner
from ex04.services.comparison.report_gen import ReportGenerator
from ex04.services.comparison.signed_metrics import SignedMetricsCalculator
from ex04.shared.gatekeeper import GatekeeperInterface
from ex04.shared.types import ComparisonReport, GraphData
from ex04.shared.types_experiment import ExperimentConfig, SignedMetrics


class ComparisonService(ComparisonServiceInterface):
    """Run both comparison approaches and generate a report.

    Before any provider call, FairnessEnforcer verifies that both modes
    share identical controlled-variable configurations. SignedMetrics
    (including regressions) are stored alongside the ComparisonReport.
    """

    def __init__(self, gatekeeper: GatekeeperInterface, provider: str = "openai") -> None:
        """Initialize comparison collaborators."""
        self._provider = provider
        self._naive = NaiveRunner(gatekeeper, provider)
        self._guided = GraphGuidedRunner(gatekeeper, provider)
        self._metrics = MetricsCalculator()
        self._signed = SignedMetricsCalculator()
        self._enforcer = FairnessEnforcer()
        self._reports = ReportGenerator()
        self.last_signed_metrics: SignedMetrics | None = None

    def run_comparison(
        self,
        bug_report: str,
        source_files: list[Path],
        graph_data: GraphData | None = None,
        vault_path: Path | None = None,
    ) -> ComparisonReport:
        """Run naive and graph-guided approaches and compare metrics.

        Raises FairnessViolationError before any provider call if the
        shared configuration diverges between modes. Signed deltas
        (including regressions) are stored on self.last_signed_metrics.
        """
        shared_cfg = ExperimentConfig(
            bug_report=bug_report, provider=self._provider
        )
        self._enforcer.check(shared_cfg, shared_cfg)
        naive = self._naive.run(bug_report, source_files)
        guided = self._guided.run(bug_report, graph_data, vault_path)
        self.last_signed_metrics = self._signed.compute(naive, guided)
        return self._reports.generate(self._metrics.compare(naive, guided))
