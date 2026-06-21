"""Comparison service facade for canonical naive vs graph-guided runs."""

from __future__ import annotations

from collections.abc import Sequence
from pathlib import Path

from ex04.services.comparison.artifacts import persist_outcome
from ex04.services.comparison.fairness import FairnessEnforcer
from ex04.services.comparison.graph_diff.models import PostGraphStatus
from ex04.services.comparison.graph_guided_runner import GraphGuidedRunner
from ex04.services.comparison.interface import ComparisonServiceInterface
from ex04.services.comparison.metrics import MetricsCalculator
from ex04.services.comparison.naive_runner import NaiveRunner
from ex04.services.comparison.report_gen import ReportGenerator
from ex04.services.comparison.request_utils import strategy_request
from ex04.services.comparison.result_metrics import result_to_run_metrics
from ex04.services.comparison.signed_metrics import SignedMetricsCalculator
from ex04.services.comparison.trace import TraceRecorder
from ex04.shared.gatekeeper import GatekeeperInterface
from ex04.shared.types import ComparisonReport, GraphData
from ex04.shared.types_experiment import ComparisonOutcome, SignedMetrics
from ex04.shared.types_request import ComparisonRequest
from ex04.shared.types_results import InvestigationResult


class ComparisonService(ComparisonServiceInterface):
    """Run comparison approaches with pre-call fairness enforcement."""

    def __init__(self, gatekeeper: GatekeeperInterface, provider: str = "openai") -> None:
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
        request: ComparisonRequest | str,
        source_files: Sequence[Path],
        graph_data: GraphData | None = None,
        vault_path: Path | None = None,
        *,
        post_graph: GraphData | None = None,
        post_graph_status: PostGraphStatus | None = None,
        post_graph_error: str = "",
    ) -> ComparisonOutcome | ComparisonReport:
        """Run both modes; legacy string input returns the old report type."""
        if isinstance(request, str):
            legacy = ComparisonRequest(
                bug_report=request,
                provider=self._provider,
                run_id="legacy-comparison",
            )
            outcome = self._run_canonical(
                legacy, source_files, graph_data, vault_path, persist=False
            )
            return self._legacy_report(outcome)
        return self._run_canonical(
            request, source_files, graph_data, vault_path,
            post_graph=post_graph,
            post_graph_status=post_graph_status,
            post_graph_error=post_graph_error,
        )

    def run_naive_investigation(
        self,
        request: ComparisonRequest,
        source_files: Sequence[Path],
    ) -> InvestigationResult:
        """Public single-mode operation for SDK delegation."""
        request.validate()
        return self._naive.run(strategy_request(request, "naive"), source_files)

    def run_graph_investigation(
        self,
        request: ComparisonRequest,
        graph_data: GraphData | None = None,
        vault_path: Path | None = None,
    ) -> InvestigationResult:
        """Public graph-mode operation for SDK delegation."""
        request.validate()
        return self._guided.run(strategy_request(request, "graph"), graph_data, vault_path)

    def compute_metrics(
        self,
        naive: InvestigationResult,
        guided: InvestigationResult,
    ) -> SignedMetrics:
        """Public signed-metrics operation for SDK delegation."""
        return self._signed.compute(result_to_run_metrics(naive), result_to_run_metrics(guided))

    def _run_canonical(
        self,
        request: ComparisonRequest,
        source_files: Sequence[Path],
        graph_data: GraphData | None,
        vault_path: Path | None,
        persist: bool = True,
        post_graph: GraphData | None = None,
        post_graph_status: PostGraphStatus | None = None,
        post_graph_error: str = "",
    ) -> ComparisonOutcome:
        request.validate()
        config_hash = request.controlled_config_hash()
        naive_req = strategy_request(request, "naive", run_id=f"{request.run_id}-naive")
        guided_req = strategy_request(request, "graph", run_id=f"{request.run_id}-graph")
        self._enforcer.check(naive_req, guided_req)
        naive_trace = TraceRecorder(naive_req.run_id)
        guided_trace = TraceRecorder(guided_req.run_id)
        naive = self._naive.run(naive_req, source_files, trace=naive_trace)
        guided = self._guided.run(guided_req, graph_data, vault_path, trace=guided_trace)
        naive.config_hash = guided.config_hash = config_hash
        self.last_signed_metrics = self._signed.compute(
            result_to_run_metrics(naive),
            result_to_run_metrics(guided),
        )
        outcome = ComparisonOutcome(
            naive_result=naive,
            guided_result=guided,
            signed_metrics=self.last_signed_metrics,
            config_hash=config_hash,
            evidence_class=request.evidence_class,
            limitations=naive.limitations + guided.limitations,
        )
        if persist:
            return persist_outcome(
                outcome,
                request,
                naive_trace,
                guided_trace,
                graph_data,
                post_graph,
                post_graph_status,
                post_graph_error,
            )
        return outcome

    def _legacy_report(self, outcome: ComparisonOutcome) -> ComparisonReport:
        naive_rm = result_to_run_metrics(outcome.naive_result)
        guided_rm = result_to_run_metrics(outcome.guided_result)
        return self._reports.generate(self._metrics.compare(naive_rm, guided_rm))
