# EX04 — Reverse Engineering, Debugging & Token-Efficient Agentic AI

A LangGraph-based AI agent that investigates bugs in unfamiliar codebases by
combining **code-graph analysis** ([Grphify](https://pypi.org/project/graphifyy/))
with **knowledge management** (an Obsidian vault), and then proves the token
savings of a graph-guided approach versus a naive full-corpus one.

> **Course**: AI Orchestration, Exercise 04 · **Package**: `ex04` · **Version**: 1.00
> The authoritative assignment spec lives in [`ASSIGNMENT.md`](ASSIGNMENT.md).

## Why

A naive bug investigation feeds large swaths of source code to an LLM. This
project instead builds a structural graph of the codebase once, navigates it to
locate the few entities relevant to a bug, and feeds only those to the model —
then measures the difference in tokens (and therefore cost).

## Architecture

The codebase follows an **SDK-first** design: all business logic is reached
through a single SDK entry point, and every external API call flows through a
central gatekeeper.

| Layer | Location | Responsibility |
|---|---|---|
| SDK | `src/ex04/sdk/` | Single entry point; orchestrates services (Phase 5) |
| Shared | `src/ex04/shared/` | Config, API gatekeeper, rate limiting, token tracking, types |
| Providers | `src/ex04/providers/` | Pluggable LLM providers (OpenAI, Anthropic) |
| Graph service | `src/ex04/services/graph/` | Run Grphify, parse `graph.json`, analyze structure |
| Vault service | `src/ex04/services/vault/` | Build/navigate the Obsidian knowledge vault |
| Agent service | `src/ex04/services/agent/` | LangGraph bug-investigation workflow |
| Analysis / Comparison | `src/ex04/services/{analysis,comparison}/` | Reverse-engineering artifacts; naive-vs-guided token comparison |

All configuration is externalized to `config/setup.json` and
`config/rate_limits.json` — nothing is hardcoded.

## Prerequisites

- Python ≥ 3.12
- [`uv`](https://docs.astral.sh/uv/) for dependency management (required — do not use `pip`/`venv`)
- The Grphify skill, if you intend to build graphs from your AI assistant:

  ```bash
  uv run graphify install claude
  ```

## Setup

```bash
uv sync                 # create the venv and install ex04 + dependencies
cp .env.example .env    # if present; otherwise set provider API keys in your env
```

Set the relevant provider key (`OPENAI_API_KEY` or `ANTHROPIC_API_KEY`) per
`config/setup.json`.

## Building a code graph

The graph service shells out to the real Grphify CLI:

```bash
# Full AST + semantic extraction (needs an LLM backend / API key):
uv run graphify extract <path-to-target-repo>
# AST-only, no LLM:
uv run graphify update <path-to-target-repo> --no-cluster
```

Grphify writes `graph.json` (NetworkX node-link format) and `GRAPH_REPORT.md`
to `<path>/graphify-out/`. `GraphParser` reads that artifact into typed
`GraphData` (entities, relationships, node-level communities).

## Testing

```bash
uv run pytest                 # full suite with coverage gate (>=85%)
uv run pytest tests/unit/services/graph -v
uv run ruff check             # zero violations required
```

Graph-service tests validate against a **real** committed Grphify artifact
(`tests/fixtures/graph/sample_graph.json`), not synthetic JSON.

## Documentation

| Document | Purpose |
|---|---|
| [`ASSIGNMENT.md`](ASSIGNMENT.md) | Assignment spec, grading criteria, deliverables |
| [`docs/PRD.md`](docs/PRD.md) | Requirements, KPIs, scope |
| [`docs/plan-wiki/`](docs/plan-wiki/Home.md) | Architecture: C4 models, ADRs, API contracts |
| [`docs/todo-wiki/`](docs/todo-wiki/Home.md) | 8-phase task plan |
| [`docs/PROMPT_LOG.md`](docs/PROMPT_LOG.md) | AI-assisted development log |

## Status

Implemented: project foundation, shared layer (config, gatekeeper, token
tracking), provider layer, and the **graph service** (runner, parser,
analyzer). In progress: vault service, analysis/agent services, the SDK
façade, and the CLI entry point (`main.py`). See the
[todo-wiki](docs/todo-wiki/Home.md) for the live task board.
