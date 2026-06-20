"""Generate fixture-labeled comparison charts for the experiment report.

All charts display "[FIXTURE DEMONSTRATION — not live evidence]" labels
since token telemetry is blocked (no live LLM calls possible).

Usage: uv run python scripts/generate_charts.py

Traceability: [TODO P8-R06]
"""

from __future__ import annotations

import json
from pathlib import Path

import matplotlib  # noqa: I001
import matplotlib.pyplot as plt

matplotlib.use("Agg")  # non-interactive; call before any plt.show()

ROOT = Path(__file__).parent.parent
ARTS = ROOT / "artifacts"
CHARTS = ROOT / "assets" / "charts"
DIAGRAMS = ROOT / "assets" / "diagrams"

FIXTURE_LABEL = "[FIXTURE DEMONSTRATION — not live evidence]"
COLORS = {"naive": "#E07B39", "graph": "#3B7DD8"}


def _load_manifests() -> tuple[dict, dict]:
    naive = json.loads((ARTS / "manifests" / "fixture-naive-001_manifest.json").read_text())
    guided = json.loads((ARTS / "manifests" / "fixture-001_manifest.json").read_text())
    return naive, guided


def _fig_header(ax: plt.Axes, title: str) -> None:
    ax.set_title(title, fontsize=13, fontweight="bold", pad=12)
    ax.text(0.5, -0.13, FIXTURE_LABEL, transform=ax.transAxes,
            ha="center", fontsize=8, color="#CC0000", style="italic")


def generate_files_chart(naive: dict, guided: dict) -> Path:
    """Bar chart: files read per mode."""
    fig, ax = plt.subplots(figsize=(6, 4))
    modes = ["Naive", "Graph-guided"]
    values = [naive["files_read"], guided["files_read"]]
    colors = [COLORS["naive"], COLORS["graph"]]
    bars = ax.bar(modes, values, color=colors, width=0.4, edgecolor="white")
    for bar, val in zip(bars, values, strict=True):
        ax.text(bar.get_x() + bar.get_width() / 2, bar.get_height() + 0.1,
                str(val), ha="center", va="bottom", fontweight="bold")
    ax.set_ylabel("Files read")
    ax.set_ylim(0, max(values) * 1.3)
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    _fig_header(ax, "Files Read per Investigation Mode")
    fig.tight_layout(rect=[0, 0.05, 1, 1])
    out = CHARTS / "files_read_comparison.png"
    fig.savefig(out, dpi=150, bbox_inches="tight")
    plt.close(fig)
    return out


def generate_iterations_chart(naive: dict, guided: dict) -> Path:
    """Bar chart: iterations per mode."""
    fig, ax = plt.subplots(figsize=(6, 4))
    modes = ["Naive", "Graph-guided"]
    values = [naive["iterations"], guided["iterations"]]
    colors = [COLORS["naive"], COLORS["graph"]]
    bars = ax.bar(modes, values, color=colors, width=0.4, edgecolor="white")
    for bar, val in zip(bars, values, strict=True):
        ax.text(bar.get_x() + bar.get_width() / 2, bar.get_height() + 0.01,
                str(val), ha="center", va="bottom", fontweight="bold")
    ax.set_ylabel("Iterations")
    ax.set_ylim(0, max(values) * 1.5 + 1)
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    _fig_header(ax, "Iterations per Investigation Mode")
    fig.tight_layout(rect=[0, 0.05, 1, 1])
    out = CHARTS / "iterations_comparison.png"
    fig.savefig(out, dpi=150, bbox_inches="tight")
    plt.close(fig)
    return out


def generate_tokens_blocked_chart() -> Path:
    """Placeholder chart showing token telemetry is blocked."""
    fig, ax = plt.subplots(figsize=(6, 4))
    ax.text(0.5, 0.55, "Token Telemetry", ha="center", va="center",
            fontsize=16, fontweight="bold", transform=ax.transAxes)
    ax.text(0.5, 0.42, "BLOCKED", ha="center", va="center",
            fontsize=22, fontweight="bold", color="#CC0000", transform=ax.transAxes)
    ax.text(0.5, 0.30, "No live LLM calls (no API keys)\nToken counts unavailable",
            ha="center", va="center", fontsize=10, color="#555555",
            transform=ax.transAxes)
    ax.axis("off")
    _fig_header(ax, "Token Comparison")
    fig.tight_layout(rect=[0, 0.05, 1, 1])
    out = CHARTS / "tokens_comparison.png"
    fig.savefig(out, dpi=150, bbox_inches="tight")
    plt.close(fig)
    return out


def generate_architecture_diagram() -> Path:
    """Generate Mermaid architecture diagram as a Markdown file."""
    mermaid = """```mermaid
graph TB
    CLI["CLI (__main__.py)"] --> SDK["Ex04SDK\n(sdk.py + mixins)"]
    SDK --> GK["ApiGatekeeper\n(gatekeeper.py)"]
    SDK --> CMP["ComparisonService\n(service.py)"]
    SDK --> GRAPH["GraphService\n(graph/service.py)"]
    SDK --> VAULT["VaultService\n(vault/service.py)"]
    SDK --> AGENT["AgentService\n(agent/service.py)"]
    CMP --> NR["NaiveRunner"]
    CMP --> GR["GraphGuidedRunner"]
    CMP --> FE["FairnessEnforcer"]
    CMP --> SM["SignedMetricsCalculator"]
    CMP --> RG["ReportGenerator"]
    GR --> CB["_context_builder.py"]
    GR --> OP["_output_parser.py"]
    NR --> OP
    GK --> PROV["Providers\n(anthropic/openai)"]
    GRAPH --> GFY["Graphify CLI\n(python -m graphify extract)"]
    SDK --> AS["ArtifactStore"]
    SDK --> CG["CorrectnessGate"]
```"""
    out = DIAGRAMS / "architecture.md"
    out.write_text(
        f"# Architecture Diagram\n\n> {FIXTURE_LABEL}\n\n{mermaid}\n",
        encoding="utf-8",
    )
    return out


def main() -> None:
    """Generate all charts and diagrams."""
    CHARTS.mkdir(parents=True, exist_ok=True)
    DIAGRAMS.mkdir(parents=True, exist_ok=True)
    naive, guided = _load_manifests()
    paths = [
        generate_files_chart(naive, guided),
        generate_iterations_chart(naive, guided),
        generate_tokens_blocked_chart(),
        generate_architecture_diagram(),
    ]
    for p in paths:
        print(f"  wrote {p.relative_to(ROOT)}")
    print("Charts and diagrams generated.")


if __name__ == "__main__":
    main()
