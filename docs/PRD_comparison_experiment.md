# PRD — Controlled Comparison Experiment

| Field | Value |
|---|---|
| **Requirement ID** | PRD-CE |
| **Parent PRD** | [docs/PRD.md](PRD.md) §5.6 (FR-6.1–FR-6.4) |
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
| `request` | `ComparisonRequest` | Canonical validated experiment contract |

---

## Outputs

| Output | Type | Description |
|---|---|---|
| `ComparisonOutcome` | dataclass | Naive result, graph result, signed metrics, manifests, reports |
| Run manifest JSON | file | Machine-readable ledger per run |
| Comparison Markdown | file | Human-readable `artifacts/runs/<run-id>/reports/comparison.md` |

---

## Controlled vs. Treatment Field Classification

The comparison experiment isolates **one** intentional experimental treatment: the context-acquisition strategy.

### Controlled (shared by both modes — must be identical)

| Field | Notes |
|---|---|
| Provider | Same provider name and base URL |
| Model | Same model identifier |
| Generation parameters | Temperature, max tokens, top-p, stop sequences |
| System instructions | Same template and version |
| Prompt envelope | Same canonical template and version (`prompt_envelope_version`) |
| Response/output schema | Same response parser and output schema version |
| Gatekeeper boundary | Both modes route through the same `ApiGatekeeper` |
| Retry policy | Same retry count, backoff, and error handling |
| Token-record conversion | Same `TokenRecord` constructor from `ProviderResponse` |
| Budget ledger | Same cumulative budget accounting (`BudgetLedger`) |
| Trace event creation | Same `ProviderTraceEvent` factory |
| Correctness gate | Same `CorrectnessGate` logic and version |
| Artifact schema | Same `RunManifest` and report schemas |
| Failure representation | Same `RunMetrics` fields for partial/failed runs |

### Treatment (intentionally different)

| Field | Naive | Graph-Guided |
|---|---|---|
| Context acquisition strategy | Read raw source files without graph guidance | Navigate graph + vault; use ranked entities, dependency paths, and source anchors |
| Resulting `ContextBundle` | Flat source content, bounded by naive file limit | Graph-ranked, vault-enriched, source-anchored context |

## Parity Fingerprint

A deterministic parity fingerprint is computed before provider calls and must match across both modes:

```python
@dataclass(frozen=True, slots=True)
class ParityFingerprint:
    provider: str
    model: str
    generation_params_hash: str   # SHA-256 of generation parameters
    system_prompt_version: str
    prompt_envelope_version: str
    response_schema_version: str
    retry_policy_hash: str
    budget_policy_hash: str
    correctness_gate_version: str
```

If the parity fingerprint mismatches between modes before provider calls, comparison execution shall raise `ParityMismatchError` and abort — no provider calls shall occur.

## Shared Instrumented Call Service

Both modes shall delegate provider calls through a shared `InstrumentedCallService` that produces an atomic result:

```python
@dataclass(frozen=True, slots=True)
class InstrumentedCallResult:
    response: ProviderResponse
    token_record: TokenRecord
    trace_event: ProviderTraceEvent
```

This design prevents a call path where a provider call succeeds but telemetry is forgotten because recording was a separate optional step.

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
- Full SHA-256 controlled configuration hash

**Naive mode must not** use: graph rankings, vault notes, graph relationships, or graph-selected anchors.

**Graph-guided mode must** use: ranked entities, dependency paths, vault notes (index.md, hot.md), and source anchors traceable to file+line.

## Graph-Diff Report Integration

When both a pre-fix and a post-fix graph snapshot are available, the comparison report shall include a graph-diff section classifying entity, relationship, and community changes.

When the post-fix graph is unavailable, the report shall render an explicit `BLOCKED` or `MISSING` section with a typed status, not silence. The comparison token metrics shall remain available regardless of graph-diff availability.

Planned artifact paths:
- `artifacts/runs/<run-id>/reports/graph_diff.json`
- `artifacts/runs/<run-id>/reports/graph_diff.md`

---

## Invariants

- Neither mode reads the same file more than once per run.
- Token counts come from provider response metadata only; they are never estimated.
- Unavailable telemetry fields are represented as `null` — never fabricated.
- Negative savings (regression) are reported as-is; never clamped to zero.
- Parsed structured output with valid anchors is only a `grounded_candidate`.
- A diagnosis is `verified` only when the deterministic correctness gate passes.

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

- [ ] `ComparisonService.run_comparison` returns a validated `ComparisonOutcome`.
- [ ] Both modes accept identical configuration and bug report.
- [ ] Fairness invariants are tested in `tests/unit/services/comparison/test_fairness.py`.
- [ ] Reports saved to `artifacts/runs/<run-id>/reports/comparison.{json,md}`.
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
- Deterministic fixture tests: `ComparisonOutcome` and reports round-trip through JSON serialization.

---

## Evidence Requirements

- `artifacts/runs/<run-id>/reports/comparison.md` produced after a real or fixture-based run.
- `artifacts/manifests/` contains at least one valid manifest JSON.
- `tests/unit/services/comparison/test_fairness.py` passes with 0 failures.

---

## Revision History

| Version | Date | Change |
|---|---|---|
| 1.0 | 2026-06-20 | Initial creation for Phase 6 finalization |
| 1.1 | 2026-06-21 | Align with `ComparisonRequest`/`ComparisonOutcome`, grounded/verified semantics, and run-scoped reports. |
| 1.2 | 2026-06-21 | Add controlled-vs-treatment field classification, parity fingerprint definition, shared `InstrumentedCallService`, pre-call mismatch rejection semantics, and graph-diff report integration. Traceability: [PRD §5.6 FR-6.4]. |
