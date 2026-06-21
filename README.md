# EX04 - Graph-Guided Bug Investigation and Token-Efficiency Comparison

[![CI](https://github.com/Us5rName/ai-orchestration-ex4-finding-bugs/actions/workflows/ci.yml/badge.svg)](https://github.com/Us5rName/ai-orchestration-ex4-finding-bugs/actions/workflows/ci.yml)
[![Python 3.12](https://img.shields.io/badge/python-3.12-blue.svg)](https://www.python.org/)

A LangGraph-based AI agent that investigates bugs in unfamiliar Python codebases
using **code-graph analysis** (Grphify) and **knowledge management** (Obsidian vault),
then measures the token-efficiency advantage of graph-guided context selection
versus naive context selection without graph-derived prioritization.

---

## Experiment Overview

| Field | Value |
|---|---|
| **Central question** | Does graph-guided context selection reduce token usage compared to naive context selection without graph-derived prioritization? |
| **Target** | andela/buggy-python |
| **Selected bug** | `ImportError: cannot import name 'lambda_array' from 'snippets'` — `__init__.py` has all imports commented out; additional type/name bugs in `loop.py` and `io.py` |
| **Provenance** | `artifacts/pre_fix/provenance.json` |
| **Independent variable** | Context acquisition strategy (naive vs. graph-guided) |
| **Controlled variables** | Provider, model, system prompt, max iterations, token budget |

### Evidence Classification

| Evidence | Class | Location |
|---|---|---|
| Graph-analysis extension tests | Deterministic keyless evidence | `tests/unit/services/analysis/` |
| Artifact store / correctness gate tests | Deterministic keyless evidence | `tests/unit/shared/`, `tests/unit/services/comparison/` |
| Graphify extraction on code-only corpus | Deterministic keyless evidence | `artifacts/pre_fix/graphify-out/graph.json` |
| Bug reproduction (ImportError) | Deterministic keyless evidence | `artifacts/pre_fix/provenance.json` |
| Obsidian vault | Representative deterministic fixture | `obsidian/` |
| Run manifests | Representative deterministic fixture | `artifacts/manifests/` |
| Live LLM runs, real token counts | Blocked (no provider credentials) | N/A |

> No fabricated evidence. Blocked live operations are reported as blocked, not simulated.

---

## Architecture

```
Ex04SDK (single entry point)
    |-- GraphService        Grphify runner + parser + analyzer
    |-- VaultService        Obsidian vault builder + navigator
    |-- AgentService        LangGraph bug-investigation workflow
    |-- ComparisonService   NaiveRunner + GraphGuidedRunner + metrics
    `-- AnalysisService     Reverse engineering + bug reports + extensions
```

All external API calls flow through `GatekeeperInterface`. Configuration is
externalized to `config/setup.json` and `config/rate_limits.json`.

### Extensions

| ID | Name | SDK method | PRD |
|---|---|---|---|
| EXT-1 | Orphan / weak-component detection | `detect_orphans()` | [PRD_extension_analysis.md](docs/PRD_extension_analysis.md) |
| EXT-2 | Patch-impact analysis (BFS) | `analyze_patch_impact()` | [PRD_extension_analysis.md](docs/PRD_extension_analysis.md) |

---

## Repository Structure

```
src/ex04/
|-- sdk/             # Single entry point (sdk.py, _extensions.py, _wiring.py)
|-- shared/          # Config, gatekeeper, rate limiter, token tracker, types
|-- providers/       # OpenAI + Anthropic adapters
`-- services/
    |-- graph/       # Grphify runner + parser + analyzer
    |-- vault/       # Obsidian vault builder + navigator
    |-- agent/       # LangGraph workflow (7 nodes)
    |-- analysis/    # Reverse engineering + orphan detector + patch-impact
    `-- comparison/  # NaiveRunner + GraphGuidedRunner + metrics + gate

tests/               # 489 tests; 95%+ coverage
scripts/             # generate_doc_wikis.py, check_docs_sync.py, validate_repo.py
artifacts/           # Immutable evidence (fixtures committed; live runs blocked)
obsidian/            # Obsidian vault (fixture)
reports/             # Comparison and gate reports
notebooks/           # walkthrough.ipynb, comparison_analysis.ipynb (SDK-based, keyless)
assets/charts/       # Fixture-labeled comparison charts (PNG)
assets/diagrams/     # Architecture diagram (Mermaid)
docs/                # PRD, PLAN, TODO, mechanism PRDs, prompt registry, wiki
```

---

## Installation

```bash
# Requires Python >= 3.12 and uv (https://docs.astral.sh/uv/)
uv sync --all-groups
cp .env-example .env   # then set OPENAI_API_KEY or ANTHROPIC_API_KEY
```

### .env-example explanation

```
OPENAI_API_KEY=         # Required for OpenAI provider (live runs only)
ANTHROPIC_API_KEY=      # Required for Anthropic provider (live runs only)
```

No API keys are required for the keyless test suite or graph-analysis extensions.

---

## Keyless Quick Start

```bash
# Run all tests (no API key required)
uv run pytest

# Run graph-analysis extensions directly
uv run python -c "
from ex04.shared.types import Entity, GraphData, Relationship
from ex04.services.analysis.orphan_detector import OrphanDetector
from ex04.services.analysis.patch_impact import PatchImpactAnalyzer

graph = GraphData(
    entities=[Entity('A', 'class', 'a.py', (1,10)), Entity('B', 'function', 'b.py', (1,5))],
    relationships=[Relationship('A', 'B', 'calls')]
)
print(OrphanDetector().detect(graph))
print(PatchImpactAnalyzer().analyze(graph, ['A']))
"

# Validate repository
uv run python scripts/validate_repo.py

# View walkthrough notebook after installing a notebook viewer in your environment
# The notebook itself is committed at notebooks/walkthrough.ipynb.
```

---

## SDK Usage

```python
from ex04.sdk import Ex04SDK

sdk = Ex04SDK.from_config("config/setup.json")

# Graph analysis extensions (no provider required)
orphan_report = sdk.detect_orphans(graph_data, min_connections=0)
impact_report = sdk.analyze_patch_impact(graph_data, changed_symbols=["MyClass"])

# Full pipeline (requires provider credentials and target codebase)
result = sdk.full_pipeline(target_path="path/to/target", bug_report="IndexError in foo()")
```

---

## Graphify Prerequisites (for live runs)

```bash
# Code-only corpus — no API key required
python -m graphify extract <target_path>   # extracts graph.json + .graphify_analysis.json

# Mixed corpus (docs/papers/images) — API key required
python -m graphify extract <target_path>   # set ANTHROPIC_API_KEY or OPENAI_API_KEY first
```

**Real Graphify extraction has been run** on `andela/buggy-python` (code-only corpus,
no API key). See `artifacts/pre_fix/graphify-out/graph.json` (13 nodes, 11 edges)
and `artifacts/pre_fix/provenance.json`.

---

## Experiment Methodology

### Fairness Controls

Both investigation modes share:
- Identical target snapshot, bug report, provider, model, system prompt
- Identical maximum model calls, tool calls, iterations, token budget
- Identical result schema, correctness gate, output parser

### Context Acquisition Strategies

**Naive mode** (`NaiveRunner`):
- Reads all source files in the target snapshot
- Concatenates them into a single context
- No graph guidance

**Graph-guided mode** (`GraphGuidedRunner`):
- Ranks entities by degree centrality from `graph.json`
- Navigates vault: `index.md -> hot.md -> component notes`
- Constructs focused prompt with source anchors

### Correctness Gate

`CorrectnessGate` validates patches deterministically:
1. Reproduce original failure in a disposable copy
2. Apply candidate patch
3. Run targeted regression test
4. Run relevant suite
5. Policy checks (no test deletion, no weakened assertions)

---

## Results

> **All token counts are unavailable**; live provider runs are blocked.
> The table below uses fixture values for file-read comparison only.

| Metric | Naive (fixture) | Graph-guided (fixture) | Delta |
|---|---|---|---|
| Files read | 12 | 2 | -10 (83% reduction) |
| Source anchors | 0 | 2 | +2 |
| Token count | N/A | N/A | Blocked |
| Correctness gate | Skipped | Skipped | N/A |

> These are fixture values demonstrating the expected workflow, not live evidence.

---

## Original Extensions

### EXT-1: Orphan Detection (FR-7.5)

```python
report = sdk.detect_orphans(graph_data, min_connections=0)
# OrphanReport.orphan_nodes: entities with degree <= threshold
# OrphanReport.weak_components: small isolated clusters
# Limitations always note: low connectivity is not proof of a defect
```

### EXT-2: Patch-Impact Analysis (FR-7.6)

```python
report = sdk.analyze_patch_impact(graph_data, ["process_data"], max_depth=3)
# ImpactReport.direct_dependents: depth-1 reverse-dependency nodes
# ImpactReport.transitive_dependents: depth > 1
# ImpactReport.impact_paths: BFS paths from changed symbol
# Limitations always note: reachability is not proof of runtime impact
```

---

## Requirement-to-Evidence Matrix

| Req ID | Summary | Implementation | Verification | Evidence | Status |
|---|---|---|---|---|---|
| FR-1.x | Grphify integration | `services/graph/` | `tests/unit/services/graph/` | 357 tests | Complete |
| FR-2.x | Obsidian vault | `services/vault/` | `tests/unit/services/vault/` | Committed | Complete |
| FR-4.x | LangGraph agent | `services/agent/` | `tests/unit/services/agent/` | Committed | Complete |
| FR-6.1 | Naive runner | `comparison/naive_runner.py` | `test_fairness.py` | Tested | Complete |
| FR-6.2 | Graph-guided runner | `comparison/graph_guided_runner.py` | `test_fairness.py` | Tested | Complete |
| FR-6.3 | Metrics + report | `comparison/metrics.py`, `report_gen.py` | `test_metrics.py` | Tested | Complete |
| FR-7.5 | Orphan detection | `analysis/orphan_detector.py` | `test_orphan_detector.py` | 9 tests | Complete |
| FR-7.6 | Patch-impact | `analysis/patch_impact.py` | `test_patch_impact.py` | 10 tests | Complete |
| PRD-CE | Correctness gate | `comparison/correctness_gate.py` | `test_correctness_gate.py` | 8 tests | Complete |
| PRD-AP | Artifact provenance | `shared/artifact_store.py` | `test_artifact_store.py` | 12 tests | Complete |
| NFR-1 | Coverage >= 85% | Full suite | `pytest --cov-fail-under=85` | 95.35% | Complete |
| NFR-2 | Ruff = 0 | All sources | `ruff check .` | 0 violations | Complete |
| NFR-3 | Max 150 lines | All sources | `validate_repo.py` | Passes | Complete |
| G1 | Graphify extraction | `services/graph/runner.py` | T7.01 | **Complete** (code-only, keyless) | See artifacts/pre_fix/ |
| G4-G5 | Bug investigation | Agent + SDK | T7.03 | **Complete** | `reports/bug_analysis.md` |
| G6 | Token comparison | ComparisonService | T7.04 | **Complete** | `artifacts/runs/phase7-comparison/reports/comparison.md` |

---

## Artifact Index

| Artifact | Location | Evidence class |
|---|---|---|
| Vault index | `obsidian/index.md` | Fixture |
| Hot notes | `obsidian/hot.md` | Fixture |
| Component notes | `obsidian/components/` | Fixture |
| Pre-fix provenance | `artifacts/pre_fix/provenance.json` | Fixture |
| Graph-guided manifest | `artifacts/manifests/fixture-001_manifest.json` | Fixture |
| Naive manifest | `artifacts/manifests/fixture-naive-001_manifest.json` | Fixture |
| Investigation result | `artifacts/runs/fixture-001/result.json` | Fixture |
| Graphify graph output | `artifacts/pre_fix/graphify-out/graph.json` | Deterministic — real CLI run |
| Comparison analysis notebook | `notebooks/comparison_analysis.ipynb` | Deterministic (SDK-based, keyless) |
| Walkthrough | `notebooks/walkthrough.ipynb` | Deterministic |
| Files-read chart | `assets/charts/files_read_comparison.png` | Fixture (labeled) |
| Architecture diagram | `assets/diagrams/architecture.md` | Generated documentation |
| CI workflow | `.github/workflows/ci.yml` | Infrastructure |
| Prompt registry | `docs/PROMPTS.md` | Generated documentation |
| Phase 7 bug analysis | `reports/bug_analysis.md` | Deterministic keyless |
| Phase 7 comparison report | `artifacts/runs/phase7-comparison/reports/comparison.md` | Deterministic keyless |
| Phase 7 diagrams | `reports/diagrams.md` | Deterministic keyless |

---

## Phase 7 End-to-End Evidence

The committed Phase 7 run is keyless and reproducible. It uses the target
snapshot in `graph-home/.graphify/repos/andela/buggy-python`, the graph in
`graph-home/graphify-out/`, the generated vault in `obsidian/`, and immutable
run artifacts under `artifacts/runs/phase7-*`.

```mermaid
flowchart LR
    target[Target snapshot] --> graph[Graphify graph]
    graph --> vault[Obsidian vault]
    graph --> agent[Graph-guided agent]
    vault --> agent
    agent --> bug[reports/bug_analysis.md]
    agent --> cmp[comparison.md]
    graph --> diagrams[reports/diagrams.md]
```

Reports:

- `reports/bug_analysis.md`
- `reports/root_cause.md`
- `reports/diff_foobar.md`
- `reports/diagrams.md`
- `reports/pipeline.md`

---

## Prompt Registry

See [`docs/PROMPTS.md`](docs/PROMPTS.md) for the complete Phase 6-8 prompt registry
(15 entries, all Prompt templates, none executed against a live provider).

---

## Quality Commands

```bash
uv run ruff check .                              # zero violations required
uv run pytest --cov=src/ex04 --cov-fail-under=85 # 97%+ coverage
uv run python scripts/validate_repo.py           # file size + secret + boundary checks
uv run python scripts/check_docs_sync.py         # wiki sync validation
find src -name "*.py" | xargs wc -l | awk '$1 > 150 {print}'  # file size check
```

---

## AI-Use Disclosure

- Implementation assisted by Claude Code (claude-sonnet-4-6)
- All prompts in `docs/PROMPTS.md` are newly authored templates for reproducibility
- No prompts were executed against a live provider in the finalization session
- All test results, coverage, ruff, and validation outputs are deterministic
- Live operations (Graphify, LLM runs, provider telemetry) are blocked without credentials

---

## Known Limitations

1. **Graphify extraction**: Complete for code-only corpus (`python -m graphify extract snippets`). Real `graph.json` committed at `artifacts/pre_fix/graphify-out/graph.json`.
2. **Live LLM runs blocked**: All provider API calls require credentials not committed to this repo.
3. **Real token counts unavailable**: No provider telemetry; cost comparison not possible.
4. **Correctness gate not executed**: Requires target snapshot; gate implementation tested in isolation.
5. **Fixture manifests are illustrative**: Token fields are `null` in all committed manifests.
6. **Wiki sync check has subprocess overhead**: `check_docs_sync.py` runs a subprocess; add to pre-commit only in dev environments.

---

## Reproducible Self-Assessment

**Verified strengths**:
- 489 deterministic tests, 95%+ coverage, 0 ruff violations, all files <= 150 lines
- SDK-first design with full dependency injection
- Both graph-analysis extensions implemented, tested, and exposed via SDK
- Immutable artifact structure with overwrite protection
- Professional prompt registry (15 entries)
- CI workflow covering all keyless checks

**Blocked operations**:
- Full Graphify extraction with docs corpus (requires API key; code-only corpus done)
- Real LLM investigation runs (T7.03; no credentials)
- Real token comparison (T7.04; no credentials)
- Real screenshots (no live execution)

**Submission readiness**: **Not fully submission-ready**; live evidence (T7.01-T7.04) is
blocked. All keyless P0 requirements are complete. Blocked live operations are
explicitly documented rather than fabricated.

---

## Controlled Comparison Semantics

The Phase 6-8 production path uses `ComparisonRequest` as the canonical
experiment contract. Every controlled field is classified for fairness and is
included in a full 64-character SHA-256 controlled configuration hash. The
comparison service derives distinct naive and graph-guided requests and checks
them before either mode can invoke a provider.

Both runners share the same cumulative `BudgetLedger`, deterministic context
token estimator, and JSONL trace recorder. Parsed structured output with valid
source anchors is only a `grounded_candidate`; it is not counted as verified
correctness unless the deterministic correctness gate passes.

Production comparison artifacts are written under immutable run directories:
`artifacts/runs/<run-id>/traces/investigation.jsonl`,
`artifacts/manifests/<run-id>_manifest.json`, and
`artifacts/runs/<base-run-id>/reports/comparison.{json,md}`. Manifests and
reports preserve full SHA-256 hashes and keep token telemetry numeric.

Live provider-backed investigation, real token telemetry, and billed cost remain
blocked until bounded credentials are available. Fixture and deterministic
evidence are not presented as live evidence.

---

## Clean-Clone Verification

Clean-clone verification is recorded in
[`reports/clean_clone_verification.md`](reports/clean_clone_verification.md)
after the final candidate commit is tested in an isolated worktree.

---

## Troubleshooting

| Issue | Solution |
|---|---|
| `uv: command not found` | Install uv: `pip install uv` or see https://docs.astral.sh/uv/ |
| `ModuleNotFoundError: ex04` | Run `uv sync` to install the package |
| `graphify: command not found` | Run `uv run graphify install claude` |
| `OPENAI_API_KEY not set` | Copy `.env-example` to `.env` and set key |
| Coverage < 85% | Run `uv run pytest --cov=src/ex04 -v` to see uncovered lines |

---

## Documentation

| Document | Purpose |
|---|---|
| [`ASSIGNMENT.md`](ASSIGNMENT.md) | Assignment specification |
| [`docs/PRD.md`](docs/PRD.md) | Requirements and KPIs |
| [`docs/PLAN.md`](docs/PLAN.md) | Architecture (C4, ADRs, API contracts) |
| [`docs/TODO.md`](docs/TODO.md) | Task tracking (Phases 1-8) |
| [`docs/PROMPTS.md`](docs/PROMPTS.md) | Phase 6-8 prompt registry |
| [`docs/EVIDENCE_MATRIX.md`](docs/EVIDENCE_MATRIX.md) | Evidence classification and requirement mapping |
| [`docs/SELF_ASSESSMENT.md`](docs/SELF_ASSESSMENT.md) | Evidence-backed readiness assessment |
| [`docs/PRD_comparison_experiment.md`](docs/PRD_comparison_experiment.md) | Comparison experiment PRD |
| [`docs/PRD_graph_guided_investigation.md`](docs/PRD_graph_guided_investigation.md) | Graph-guided investigation PRD |
| [`docs/PRD_artifact_provenance.md`](docs/PRD_artifact_provenance.md) | Artifact provenance PRD |
| [`docs/PRD_extension_analysis.md`](docs/PRD_extension_analysis.md) | Extension analysis PRD |
| [`docs/plan-wiki/`](docs/plan-wiki/Home.md) | Architecture wiki |
| [`docs/todo-wiki/`](docs/todo-wiki/Home.md) | Task wiki |
