"""ComparisonOpsMixin — new SDK operations for Phase 6–8 experiment.

Extracted from Ex04SDK to stay within the 150-line limit. All 7 operations
delegate to existing runners, calculators, and store — no new logic here.

Traceability: [TODO P6-R07]
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import TYPE_CHECKING

from ex04.services.comparison.correctness_gate import CorrectnessGate
from ex04.shared.artifact_store import ArtifactStore
from ex04.shared.types import GraphData, RunMetrics
from ex04.shared.types_experiment import GateOutput, RunManifest, SignedMetrics
from ex04.shared.types_request import ComparisonRequest
from ex04.shared.types_results import InvestigationResult

if TYPE_CHECKING:
    pass


def _to_run_metrics(r: InvestigationResult) -> RunMetrics:
    """Bridge InvestigationResult → RunMetrics for SignedMetricsCalculator."""
    tokens = (r.input_tokens or 0) + (r.output_tokens or 0)
    found = r.parser_status == "parsed_ok" and r.gate_status in (
        "pass", "pass_without_gate"
    )
    return RunMetrics(
        tokens_used=tokens, files_read=r.files_read, iterations=r.iterations,
        time_seconds=r.duration_seconds, found_root_cause=found,
    )


class ComparisonOpsMixin:
    """Mixin providing new experiment-level SDK operations.

    Assumes the host class exposes: self._comparison (ComparisonService),
    self._config (dict[str, Any]).
    """

    def run_naive_investigation(
        self,
        request: ComparisonRequest,
        source_files: list[Path] | None = None,
    ) -> InvestigationResult:
        """Run the naive (no-graph) investigation for one ComparisonRequest."""
        from ex04.services.comparison.naive_runner import NaiveRunner
        runner = NaiveRunner(
            gatekeeper=self._comparison._naive.gatekeeper,  # type: ignore[attr-defined]
            provider=request.provider or "openai",
            max_files=request.max_files,
            max_bytes=request.max_bytes,
            timeout_seconds=float(request.timeout_seconds),
        )
        files = source_files or []
        result = runner.run(request.bug_report, files)
        result.run_id = request.run_id
        result.mode = "naive"
        result.config_hash = request.fixture_class
        result.target_commit = request.target_commit
        return result

    def run_graph_investigation(
        self,
        request: ComparisonRequest,
        graph_data: GraphData | None = None,
        vault_path: Path | None = None,
    ) -> InvestigationResult:
        """Run the graph-guided investigation for one ComparisonRequest."""
        from ex04.services.comparison.graph_guided_runner import GraphGuidedRunner
        runner = GraphGuidedRunner(
            gatekeeper=self._comparison._guided.gatekeeper,  # type: ignore[attr-defined]
            provider=request.provider or "openai",
        )
        result = runner.run(request.bug_report, graph_data, vault_path)
        result.run_id = request.run_id
        result.mode = "graph"
        result.config_hash = request.fixture_class
        result.target_commit = request.target_commit
        return result

    def run_experiment(
        self,
        request: ComparisonRequest,
        source_files: list[Path] | None = None,
        graph_data: GraphData | None = None,
        vault_path: Path | None = None,
    ) -> tuple[InvestigationResult, InvestigationResult, SignedMetrics]:
        """Run both modes and return (naive, guided, signed_metrics)."""
        naive = self.run_naive_investigation(request, source_files)
        guided = self.run_graph_investigation(request, graph_data, vault_path)
        metrics = self.compute_metrics(naive, guided)
        return naive, guided, metrics

    def compute_metrics(
        self,
        naive: InvestigationResult,
        guided: InvestigationResult,
    ) -> SignedMetrics:
        """Compute signed deltas between naive and graph-guided results."""
        return self._comparison._signed.compute(  # type: ignore[attr-defined]
            _to_run_metrics(naive), _to_run_metrics(guided)
        )

    def run_correctness_gate(
        self,
        request: ComparisonRequest,
        patch_diff: str,
        snapshot_path: Path | None = None,
        artifact_path: Path | None = None,
    ) -> GateOutput:
        """Validate a patch diff through the deterministic correctness gate."""
        snap = snapshot_path or Path(self._config.get("paths", {}).get("target_codebase", "."))  # type: ignore[attr-defined]
        gate = CorrectnessGate()
        return gate.validate(
            snapshot_path=snap,
            patch_diff=patch_diff,
            reproduction_command=request.gate_reproduction_command,
            expected_failure_signature=request.expected_failure_signature,
            allowed_paths=request.patch_allowed_paths,
            prohibited_paths=request.patch_prohibited_paths,
            artifact_path=artifact_path,
        )

    def save_manifest(self, manifest: RunManifest) -> Path:
        """Persist a RunManifest to the artifact store."""
        root = Path(self._config.get("artifact_root", "artifacts"))  # type: ignore[attr-defined]
        store = ArtifactStore(root)
        return store.save_manifest(manifest)

    def load_provenance(self, path: str = "artifacts/pre_fix/provenance.json") -> dict[str, object]:
        """Load provenance.json from the given path."""
        return json.loads(Path(path).read_text(encoding="utf-8"))
