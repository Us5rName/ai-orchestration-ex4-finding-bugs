# PRD — Controlled Comparison Experiment

| Field | Value |
|---|---|
| **Requirement ID** | PRD-CE |
| **Parent PRD** | [docs/PRD.md](PRD.md) §5.6 (FR-6.1–6.4) |
| **Status** | Active |
| **Date** | 2026-06-20 |

---

## Purpose

Define the contract for a scientifically defensible comparison between a **naive**
investigation (raw source reading) and a **graph-guided** investigation (graph +
vault-driven context selection) against the same bug report and target snapshot.

---

## Scope

Covers: experiment configuration, shared infrastructure, fairness invariants,
context-acquisition strategies, structured results, run ledgers, and metrics.

Out of scope: LLM provider billing details, Graphify internals, vault note format.

---

## Inputs

| Input | Type | Description |
|---|---|---|
| `bug_report` | `str` | Natural-language bug description |
| `source_files` | `list[Path]` | Discoverable Python files in target snapshot |
| `graph_data` | `GraphData \| None` | Parsed Graphify output |
| `vault_path` | `Path \| None` | Root of generated Obsidian vault |
| `config` | `dict` | Shared experiment parameters (see below) |

---

## Outputs

| Output | Type | Description |
|---|---|---|
| `ComparisonReport` | dataclass | Side-by-side metrics + narrative |
| Run manifest JSON | file | Machine-readable ledger per run |
| Comparison Markdown | file | Human-readable `reports/token_comparison.md` |

---

## Contracts and Fairness Invariants

Both modes **must share** (validated at runtime and in tests):
- Target snapshot (identical source files)
- Bug report text
- Provider and model name
- System instructions template
- Maximum model calls, tool calls, and iterations
- Context/token budget ceiling
- Correctness gate logic
- Output parser and result schema
- Manifest schema

**Naive mode must not** use: graph rankings, vault notes, graph relationships, or graph-selected anchors.

**Graph-guided mode must** use: ranked entities, dependency paths, vault notes (index.md, hot.md), and source anchors traceable to file+line.

---

## Invariants

- Neither mode reads the same file more than once per run.
- Token counts come from provider response metadata only; they are never estimated.
- Unavailable telemetry fields are represented as `null` — never fabricated.
- Negative savings (regression) are reported as-is; never clamped to zero.

---

## Failure Behavior

| Condition | Behavior |
|---|---|
| Provider unavailable | Run returns `RunMetrics` with `telemetry_available=False` |
| Zero files found | Naive run returns `files_read=0`, comparison still proceeds |
| Zero denominator in savings | Savings percentage reported as `null` |
| Partial run | Manifest records `status=partial`; run is still compared |

---

## Security Constraints

- No API keys in manifests, reports, or committed artifacts.
- Absolute local paths stripped from all outputs.
- Target snapshot is read-only; investigation does not modify it.

---

## Measurable Acceptance Criteria

- [ ] `ComparisonService.run_comparison` returns a validated `ComparisonReport`.
- [ ] Both modes accept identical configuration and bug report.
- [ ] Fairness invariants are tested in `tests/unit/services/comparison/test_fairness.py`.
- [ ] Reports saved to `reports/token_comparison.md`.
- [ ] Run manifest saved to `artifacts/manifests/`.
- [ ] Negative savings are preserved in the report.

---

## Alternatives Considered

| Alternative | Reason rejected |
|---|---|
| Run modes in separate processes | Unnecessary complexity; mocking boundary is cleaner |
| Use LangChain instead of direct provider | Adds non-determinism; harder to control token counts |

---

## Testing Strategy

- Unit tests: fairness-invariant validation, metrics edge cases (zero denominators, negatives).
- Integration tests: end-to-end with mock provider confirming identical config injection.
- Deterministic fixture tests: `ComparisonReport` round-trips through JSON serialization.

---

## Evidence Requirements

- `reports/token_comparison.md` committed after first real or fixture-based run.
- `artifacts/manifests/` contains at least one valid manifest JSON.
- `tests/unit/services/comparison/test_fairness.py` passes with 0 failures.

---

## Revision History

| Version | Date | Change |
|---|---|---|
| 1.0 | 2026-06-20 | Initial creation for Phase 6 finalization |
