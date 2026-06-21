"""Artifact persistence helpers for production comparison outcomes."""

from __future__ import annotations

import hashlib
import json
from dataclasses import asdict
from pathlib import Path

from ex04.services.comparison.graph_diff import diff_graphs, render_graph_diff
from ex04.services.comparison.graph_diff.models import GraphDiffArtifacts
from ex04.services.comparison.report_gen import write_comparison_reports
from ex04.services.comparison.trace import TraceRecorder
from ex04.shared.artifact_store import ArtifactStore
from ex04.shared.types import GraphData
from ex04.shared.types_experiment import ComparisonOutcome, RunManifest
from ex04.shared.types_request import ComparisonRequest
from ex04.shared.types_results import InvestigationResult


def persist_outcome(
    outcome: ComparisonOutcome,
    request: ComparisonRequest,
    naive_trace: TraceRecorder,
    guided_trace: TraceRecorder,
    pre_graph: GraphData | None = None,
    post_graph: GraphData | None = None,
) -> ComparisonOutcome:
    """Persist traces, manifests, and reports; update outcome paths."""
    root = Path(request.artifact_root)
    store = ArtifactStore(root)
    graph_diff = diff_graphs(pre_graph, post_graph) if pre_graph is not None else None
    graph_artifacts = (
        render_graph_diff(graph_diff, root / "runs" / request.run_id)
        if graph_diff is not None
        else None
    )
    naive_trace.path, naive_trace.sha256 = naive_trace.persist(root)
    guided_trace.path, guided_trace.sha256 = guided_trace.persist(root)
    _attach_trace(outcome.naive_result, naive_trace)
    _attach_trace(outcome.guided_result, guided_trace)
    pre_graph_hash = _graph_hash(pre_graph)
    post_graph_hash = _graph_hash(post_graph)
    naive_manifest = _manifest(
        outcome.naive_result, request, graph_artifacts, pre_graph_hash, post_graph_hash
    )
    guided_manifest = _manifest(
        outcome.guided_result, request, graph_artifacts, pre_graph_hash, post_graph_hash
    )
    manifest_paths = [
        str(store.save_manifest(naive_manifest)),
        str(store.save_manifest(guided_manifest)),
    ]
    reports = write_comparison_reports(
        outcome.naive_result,
        outcome.guided_result,
        outcome.signed_metrics,
        root / "runs" / request.run_id,
        graph_diff,
    )
    report_paths = [str(path) for path in reports]
    if graph_artifacts is not None:
        report_paths.extend([
            str(graph_artifacts.json_path),
            str(graph_artifacts.markdown_path),
        ])
    outcome.manifest_paths = manifest_paths
    outcome.report_paths = report_paths
    return outcome


def _attach_trace(result: InvestigationResult, trace: TraceRecorder) -> None:
    result.trace_path = str(trace.path or "")
    result.trace_hash = trace.sha256


def _manifest(
    result: InvestigationResult,
    request: ComparisonRequest,
    graph_artifacts: GraphDiffArtifacts | None = None,
    pre_graph_hash: str = "",
    post_graph_hash: str = "",
) -> RunManifest:
    return RunManifest(
        run_id=result.run_id,
        mode=result.mode,
        provider=request.provider,
        model=request.model,
        model_params=request.model_params,
        config_hash=result.config_hash,
        shared_config_hash=result.config_hash,
        schema_version=request.schema_version,
        parser_version=request.parser_version,
        manifest_version=request.manifest_version,
        pricing_config_version=request.pricing_version,
        repo_commit=request.repo_commit,
        prompt_version=request.prompt_version,
        target_identifier=request.target_repo,
        target_commit=request.target_commit,
        target_snapshot_hash=request.target_snapshot_hash,
        input_tokens=result.input_tokens,
        output_tokens=result.output_tokens,
        total_tokens=_total_tokens(result),
        model_calls=result.model_calls,
        tool_calls=result.tool_calls,
        files_read=result.files_read,
        bytes_read=result.bytes_read,
        iterations=result.iterations,
        duration_seconds=result.duration_seconds,
        diagnosis_status=result.diagnosis_status,
        correctness_gate_status=result.gate_status,
        limitations=result.limitations,
        telemetry_available=result.telemetry_available,
        evidence_class=result.evidence_class,
        trace_path=result.trace_path,
        trace_hash=result.trace_hash,
        graph_diff_json_path=str(graph_artifacts.json_path) if graph_artifacts else "",
        graph_diff_markdown_path=str(graph_artifacts.markdown_path) if graph_artifacts else "",
        graph_diff_hash=graph_artifacts.graph_diff_hash if graph_artifacts else "",
        pre_graph_hash=pre_graph_hash,
        post_graph_hash=post_graph_hash,
    )


def _total_tokens(result: InvestigationResult) -> int | None:
    if result.input_tokens is None or result.output_tokens is None:
        return None
    return result.input_tokens + result.output_tokens


def _graph_hash(graph: GraphData | None) -> str:
    if graph is None:
        return ""
    payload = json.dumps(asdict(graph), sort_keys=True, default=str)
    return hashlib.sha256(payload.encode()).hexdigest()
