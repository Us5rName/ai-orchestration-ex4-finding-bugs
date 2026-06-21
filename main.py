"""
Ex04 — Live Pipeline Runner (Steps 3-6)

INPUTS TO CONFIGURE:
  TARGET       — path to the repo to analyse
  BUG_REPORT   — plain-text bug description
  REPORT_OUT   — output Markdown report path
  MODEL        — LLM model identifier
  BASE_URL     — provider API base URL  (OpenRouter / OpenAI / local)
  API_KEY_ENV  — env-var name for the API key (set actual key in .env)

Run: set -a && source .env && set +a && uv run python main.py
"""

import os
import subprocess
from pathlib import Path

import matplotlib
import matplotlib.pyplot as plt

from dotenv import load_dotenv

from ex04.sdk import Ex04SDK

load_dotenv()

# --- User inputs ---
TARGET      = "graph-home/.graphify/repos/andela/buggy-python"
BUG_REPORT  = (
    "All imports in snippets/__init__.py are commented out causing ImportError. "
    "Type errors in loop.py (string passed to range()) and io.py (wrong file open mode)."
)
REPORT_OUT  = Path("reports/bug_analysis_live.md")

# --- Provider (overrides config/setup.json) ---
MODEL       = "deepseek/deepseek-v3.2"
BASE_URL    = "https://openrouter.ai/api/v1"   # OpenAI: https://api.openai.com/v1
API_KEY_ENV = "OPENAI_API_KEY"
api_key = os.getenv(API_KEY_ENV)

# --- Advanced (mirrors setup.json defaults) ---
CONFIG                = "config/setup.json"
CONTEXT_WINDOW_TOKENS = 100_000
MAX_ITERATIONS        = 5
MAX_SUSPECTS          = 5


def _write_phase7_reports(reports_dir: Path, diagrams: str, inv) -> None:
    reports_dir.mkdir(parents=True, exist_ok=True)
    files = {
        "diagrams.md": diagrams,
        "root_cause.md": f"# Root Cause\n\n{inv.root_cause}\n\n## Suspects\n\n"
                         + "\n".join(f"- `{s.file_path}:{s.line_start}` (score {s.score})" for s in inv.suspects),
        "diff_foobar.md": f"# Before/After Diff\n\n```diff\n{inv.fix_diff}\n```\n",
        "pipeline.md": (
            "# Phase 7 Pipeline\n\n```mermaid\nflowchart LR\n"
            "    target[Target snapshot] --> graph[Graphify graph]\n"
            "    graph --> vault[Obsidian vault]\n"
            "    graph --> agent[Graph-guided agent]\n"
            "    vault --> agent\n"
            "    agent --> report[Bug analysis]\n"
            "    agent --> comparison[Token comparison]\n"
            "    graph --> diagrams[Reverse-engineering diagrams]\n```\n"
        ),
        "README.md": (
            "# Reports\n\n"
            "- [Bug analysis](bug_analysis_live.md)\n"
            "- [Root cause](root_cause.md)\n"
            "- [Before/after diff](diff_foobar.md)\n"
            "- [Architecture diagrams](diagrams.md)\n"
            "- [Pipeline](pipeline.md)\n"
        ),
    }
    for filename, content in files.items():
        path = reports_dir / filename
        path.write_text(content, encoding="utf-8")
        print(f"  → {path}")


def _generate_charts(report) -> None:
    """Generate bar charts from live comparison data and save to assets/charts/."""
    matplotlib.use("Agg")
    charts_dir = Path("assets/charts")
    charts_dir.mkdir(parents=True, exist_ok=True)

    naive, guided = report.metrics.naive, report.metrics.guided
    labels = ["Naive", "Graph-guided"]
    colors = ["#e07b54", "#5b9bd5"]

    specs = [
        ("tokens_comparison.png",     "Token Usage",   [naive.tokens_used,  guided.tokens_used],  "Tokens"),
        ("files_read_comparison.png",  "Files Read",    [naive.files_read,   guided.files_read],   "Files"),
        ("iterations_comparison.png",  "Iterations",    [naive.iterations,   guided.iterations],   "Iterations"),
    ]
    for filename, title, values, ylabel in specs:
        fig, ax = plt.subplots(figsize=(5, 4))
        bars = ax.bar(labels, values, color=colors, width=0.5)
        ax.bar_label(bars, fmt="%d", padding=3)
        ax.set_title(title)
        ax.set_ylabel(ylabel)
        ax.spines[["top", "right"]].set_visible(False)
        fig.tight_layout()
        fig.savefig(charts_dir / filename, dpi=150)
        plt.close(fig)
        print(f"  chart → {charts_dir / filename}")


def main() -> None:
    os.environ.setdefault("OPENAI_BASE_URL", BASE_URL)
    os.environ.setdefault("OPENAI_API_KEY_ENV", API_KEY_ENV)

    sdk = Ex04SDK.from_config(CONFIG)

    # Steps 3-6: full pipeline (graphify → vault → investigate → compare → diagrams → report)
    print("\n=== Running Full Pipeline ===")
    result = sdk.full_pipeline(TARGET, BUG_REPORT)
    print(f"{result.graph_result=}")
    print(f"{result.vault_result=}")

    inv = result.investigation
    print(f"\n--- Investigation ---")
    print(f"{inv.root_cause=}")
    print(f"{inv.suspects=}")
    print(f"{inv.token_usage.input_tokens=}")
    print(f"{inv.token_usage.output_tokens=}")
    print(f"{inv.token_usage.total_tokens=}")

    cmp = result.comparison
    naive, guided = cmp.metrics.naive, cmp.metrics.guided
    print(f"\n--- Token Comparison ---")
    print(f"{naive.tokens_used=}")
    print(f"{guided.tokens_used=}")
    print(f"{cmp.metrics.token_savings_pct=:.1f}%")
    print(f"{cmp.token_savings=}")

    # Mermaid architecture diagrams (inline)
    print(f"\n--- Architecture Diagrams ---")
    print(result.engineering)

    # Save bug report
    REPORT_OUT.parent.mkdir(parents=True, exist_ok=True)
    REPORT_OUT.write_text(result.bug_report_md, encoding="utf-8")
    print(f"\n{REPORT_OUT=}")

    # Overwrite the static fixture with live-generated diagrams
    arch_path = Path("assets/diagrams/architecture.md")
    arch_path.parent.mkdir(parents=True, exist_ok=True)
    arch_path.write_text(result.engineering, encoding="utf-8")
    print(f"{arch_path=}")

    # Phase 7 report suite (diagrams.md, root_cause.md, diff.md, pipeline.md, README.md)
    print("\n=== Generating Phase 7 Reports ===")
    reports_dir = REPORT_OUT.parent
    _write_phase7_reports(reports_dir, result.engineering, inv)

    # Bar charts from live data
    print("\n=== Generating Charts ===")
    _generate_charts(cmp)

    # Launch Jupyter Lab with both notebooks
    print("\n=== Launching Jupyter Lab ===")
    notebooks = ["notebooks/walkthrough.ipynb", "notebooks/comparison_analysis.ipynb"]
    for nb in notebooks:
        print(f"  notebook → {nb}")
    subprocess.Popen(
        ["uv", "run", "jupyter", "lab", *notebooks],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )
    print("Jupyter Lab launched in background — open http://localhost:8888")


if __name__ == "__main__":
    main()
