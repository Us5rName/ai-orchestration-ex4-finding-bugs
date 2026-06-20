"""Report Generator — comparison reports in JSON and Markdown formats.

Traceability: [TODO P7-R04]
"""

from __future__ import annotations

import hashlib
import json
from dataclasses import asdict
from pathlib import Path

from ex04.shared.types import ComparisonMetrics, ComparisonReport
from ex04.shared.types_experiment import SignedMetrics
from ex04.shared.types_results import InvestigationResult


class ReportGenerator:
    """Generate human-readable comparison summaries."""

    def generate(self, metrics: ComparisonMetrics) -> ComparisonReport:
        """Return a report with Markdown narrative and token savings."""
        token_savings = metrics.naive.tokens_used - metrics.guided.tokens_used
        narrative = (
            "| Metric | Naive | Graph-guided | Savings |\n"
            "|---|---:|---:|---:|\n"
            f"| Tokens | {metrics.naive.tokens_used} | {metrics.guided.tokens_used} | "
            f"{metrics.token_savings_pct:.1f}% |\n"
            f"| Files read | {metrics.naive.files_read} | {metrics.guided.files_read} | "
            f"{metrics.file_read_savings_pct:.1f}% |\n"
            f"| Iterations | {metrics.naive.iterations} | {metrics.guided.iterations} | "
            f"{metrics.iteration_savings_pct:.1f}% |"
        )
        return ComparisonReport(metrics=metrics, narrative=narrative, token_savings=token_savings)


def write_comparison_reports(
    naive: InvestigationResult,
    guided: InvestigationResult,
    metrics: SignedMetrics,
    artifact_path: Path,
) -> tuple[Path, Path]:
    """Write comparison.json and comparison.md to artifact_path/reports/.

    Returns (json_path, md_path). Evidence class banner is included in Markdown.
    """
    reports_dir = artifact_path / "reports"
    reports_dir.mkdir(parents=True, exist_ok=True)

    data: dict[str, object] = {
        "evidence_class": naive.evidence_class or "fixture",
        "naive_run_id": naive.run_id,
        "guided_run_id": guided.run_id,
        "naive_parser_status": naive.parser_status,
        "guided_parser_status": guided.parser_status,
        "naive_gate_status": naive.gate_status,
        "guided_gate_status": guided.gate_status,
        "signed_metrics": asdict(metrics),
        "naive_limitations": naive.limitations,
        "guided_limitations": guided.limitations,
    }
    json_text = json.dumps(data, indent=2, default=str)
    json_path = reports_dir / "comparison.json"
    json_path.write_text(json_text, encoding="utf-8")

    md_path = reports_dir / "comparison.md"
    md_path.write_text(_build_markdown(naive, guided, metrics, json_text), encoding="utf-8")
    return json_path, md_path


def _build_markdown(
    naive: InvestigationResult,
    guided: InvestigationResult,
    m: SignedMetrics,
    json_text: str,
) -> str:
    """Compose the Markdown comparison report."""
    ev_class = naive.evidence_class or "fixture"
    sha = hashlib.sha256(json_text.encode()).hexdigest()[:16]
    lines = [
        "# Comparison Report",
        "",
        f"> **Evidence Class: {ev_class.upper()}** — "
        "results are deterministic fixtures, not live LLM telemetry.",
        "",
        "## Signed Delta Table",
        "",
        "| Metric | Naive | Graph-guided | Delta |",
        "|---|---:|---:|---:|",
        f"| Tokens | {m.naive_tokens} | {m.guided_tokens} | {m.token_delta} |",
        f"| Files read | {m.naive_files} | {m.guided_files} | {m.file_delta} |",
        f"| Iterations | {m.naive_iterations} | {m.guided_iterations} | {m.iteration_delta} |",
        f"| Duration (s) | {m.naive_duration:.3f} | {m.guided_duration:.3f} "
        f"| {m.duration_delta:.3f} |",
        "",
        "## Correctness",
        "",
        "| Mode | Parser | Gate |",
        "|---|---|---|",
        f"| Naive | {naive.parser_status} | {naive.gate_status} |",
        f"| Graph-guided | {guided.parser_status} | {guided.gate_status} |",
        "",
        "## Limitations",
        "",
        *(f"- {lim}" for lim in (naive.limitations + guided.limitations + m.limitations)),
        "",
        f"*Report SHA-256 prefix: `{sha}`*",
    ]
    return "\n".join(lines) + "\n"
