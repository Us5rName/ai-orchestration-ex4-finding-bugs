"""SDK comparison operations; thin delegation over public services."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from ex04.services.comparison.correctness_gate import CorrectnessGate
from ex04.shared.artifact_store import ArtifactStore
from ex04.shared.types import GraphData, RunMetrics
from ex04.shared.types_experiment import (
    ComparisonOutcome,
    GateOutput,
    RunManifest,
    SignedMetrics,
)
from ex04.shared.types_request import ComparisonRequest
from ex04.shared.types_results import InvestigationResult


def _to_run_metrics(result: InvestigationResult) -> RunMetrics:
    """Bridge InvestigationResult to RunMetrics for legacy calculators."""
    tokens = (result.input_tokens or 0) + (result.output_tokens or 0)
    found = (
        result.verification_status == "verified"
        or result.gate_status in {"passed", "pass_without_gate"}
        or result.parser_status == "parsed_ok"
    )
    return RunMetrics(
        tokens_used=tokens,
        files_read=result.files_read,
        iterations=result.iterations,
        time_seconds=result.duration_seconds,
        found_root_cause=found,
    )


class ComparisonOpsMixin:
    """Mixin providing experiment-level SDK operations."""

    def run_naive_investigation(
        self,
        request: ComparisonRequest,
        source_files: list[Path] | None = None,
    ) -> InvestigationResult:
        """Run naive investigation through the public comparison service."""
        result = self._comparison_service().run_naive_investigation(
            request,
            source_files or [],
        )
        result.config_hash = request.controlled_config_hash()
        return result

    def run_graph_investigation(
        self,
        request: ComparisonRequest,
        graph_data: GraphData | None = None,
        vault_path: Path | None = None,
    ) -> InvestigationResult:
        """Run graph-guided investigation through the public comparison service."""
        result = self._comparison_service().run_graph_investigation(
            request,
            graph_data,
            vault_path,
        )
        result.config_hash = request.controlled_config_hash()
        return result

    def run_experiment(
        self,
        request: ComparisonRequest,
        source_files: list[Path] | None = None,
        graph_data: GraphData | None = None,
        vault_path: Path | None = None,
    ) -> ComparisonOutcome:
        """Run the canonical comparison service path."""
        outcome = self._comparison_service().run_comparison(
            request,
            source_files or [],
            graph_data,
            vault_path,
        )
        if not isinstance(outcome, ComparisonOutcome):
            raise TypeError("canonical request did not return ComparisonOutcome")
        return outcome

    def compute_metrics(
        self,
        naive: InvestigationResult,
        guided: InvestigationResult,
    ) -> SignedMetrics:
        """Compute signed deltas through the public comparison service."""
        return self._comparison_service().compute_metrics(naive, guided)

    def run_correctness_gate(
        self,
        request: ComparisonRequest,
        patch_diff: str,
        snapshot_path: Path | None = None,
        artifact_path: Path | None = None,
    ) -> GateOutput:
        """Validate a patch diff through the deterministic correctness gate."""
        snap = snapshot_path or Path(
            self._config_dict().get("paths", {}).get("target_codebase", ".")
        )
        return CorrectnessGate().validate(
            snapshot_path=snap,
            patch_diff=patch_diff,
            reproduction_command=request.gate_reproduction_command
            or request.reproduction_command,
            expected_failure_signature=request.expected_failure_signature,
            allowed_paths=request.patch_allowed_paths,
            prohibited_paths=request.patch_prohibited_paths,
            artifact_path=artifact_path,
            verification_commands=request.gate_verification_commands,
        )

    def save_manifest(self, manifest: RunManifest) -> Path:
        """Persist a RunManifest to the artifact store."""
        root = Path(self._config_dict().get("artifact_root", "artifacts"))
        return ArtifactStore(root).save_manifest(manifest)

    def load_provenance(
        self,
        path: str = "artifacts/pre_fix/provenance.json",
    ) -> dict[str, object]:
        """Load provenance.json from the given path."""
        return json.loads(Path(path).read_text(encoding="utf-8"))

    def _comparison_service(self) -> Any:
        return object.__getattribute__(self, "_comparison")

    def _config_dict(self) -> dict[str, Any]:
        return object.__getattribute__(self, "_config")
