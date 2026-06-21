<!-- GENERATED FROM CANONICAL DOCUMENTATION - DO NOT EDIT DIRECTLY -->

# 6. Phase 5 — SDK + CLI

[Back to Home](./Home.md)

**Goal**: Wire all services through SDK. Add CLI entry point.

### T5.01 — Implement SDK

| Attribute | Value |
|---|---|
| **Status** | Done |
| **Priority** | P0 |
| **PLAN Reference** | [PLAN §3.2 SDK Module] |
| **PRD Reference** | [PRD NFR-5] SDK-first |
| **Estimate** | 60 min |

**Definition of Done**:

- [x] `Ex04SDK.from_config(config_path)` creates SDK with all services
- [x] `run_graphify(target_path)` delegates to Graph Service
- [x] `build_vault(graph)` delegates to Vault Service
- [x] `investigate_bug(bug_report)` delegates to Agent Service
- [x] `run_comparison(bug_report, source_files, ...)` delegates to Comparison Service
- [x] `compare_target(target_path, bug_report)` orchestrates full comparison flow
- [x] `reverse_engineer(target_path)` delegates to Analysis Service
- [x] `generate_report(investigation)` delegates to Analysis Service
- [x] `identify_patterns(target_path)` delegates to Analysis Service
- [x] `full_pipeline(target_path, bug_report)` executes complete flow with real sources + vault
- [x] All methods have docstrings
- [x] File ≤ 150 lines — `_wiring.py` and `_comparison_inputs.py` extracted

**Independent Verification**:

```bash
uv run pytest tests/unit/sdk/test_sdk.py tests/integration/ -v
```

---

### T5.02 — Implement CLI Entry Point

| Attribute | Value |
|---|---|
| **Status** | Done |
| **Priority** | P1 |
| **PLAN Reference** | [PLAN §1.2 High-Level Architecture — CLI] |
| **Estimate** | 30 min |

**Definition of Done**:

- [x] CLI accepts commands: `graphify`, `investigate`, `compare`, `pipeline`
- [x] `compare` requires `target_path` argument; delegates to `sdk.compare_target()`
- [x] CLI loads config from `config/setup.json` (or `--config` flag)
- [x] CLI delegates all logic to SDK — no business logic in CLI
- [x] `@file` syntax supported for bug_report arguments
- [x] Exit codes: 0 success, 2 FileNotFoundError, 3 NotImplementedError, 1 other
- [x] Proper error handling and logging

**Independent Verification**:

```bash
uv run python -m ex04 --help
# Should display available commands
```

---

### T5.03 — Agent Workflow Parity Helpers

| Attribute | Value |
|---|---|
| **Status** | Done |
| **Priority** | P1 |
| **Execution Order** | 2nd of 6 remaining tasks (independent of T4.19; implemented early for fair comparison evidence) |
| **PLAN Reference** | [PLAN §3.5 Agent Service], [PLAN §3.7 Comparison Service], [PLAN ADR-008] |
| **PRD Reference** | [PRD §5.6 FR-6.4], [PRD-CE §Controlled vs. Treatment] |
| **Note** | T5.03 does NOT depend on T4.19, but is deliberately implemented early so final comparison evidence is not produced through duplicated or unfair call paths. |
| **Estimate** | 60 min |

**Purpose**: Ensure both comparison modes use the same provider-call path, telemetry, budget, trace, gate, and artifact schema. Only the context-acquisition strategy may intentionally differ. Satisfies [PRD FR-6.4] Experimental Parity.

**Planned files**:
- `src/ex04/services/comparison/call_service.py` — `InstrumentedCallService` (shared provider call)
- `src/ex04/services/comparison/prompt_builder.py` — canonical prompt envelope
- `src/ex04/services/comparison/parity.py` — `ParityFingerprint` and pre-call validation

**Key contract**:

```python
@dataclass(frozen=True, slots=True)
class InstrumentedCallResult:
    response: ProviderResponse
    token_record: TokenRecord
    trace_event: ProviderTraceEvent

@dataclass(frozen=True, slots=True)
class ParityFingerprint:
    provider: str
    model: str
    generation_params_hash: str
    system_prompt_version: str
    prompt_envelope_version: str
    response_schema_version: str
    retry_policy_hash: str
    budget_policy_hash: str
    correctness_gate_version: str
```

**Shared (controlled)**: provider, model, generation params, system instructions, prompt envelope, response schema, gatekeeper, retry policy, token-record conversion, budget ledger, trace event, correctness gate, artifact schema, failure representation.

**Different (treatment)**: context-acquisition strategy and resulting `ContextBundle`.

**Implementation subtasks**:
1. Create `call_service.py` with `InstrumentedCallService` returning atomic `InstrumentedCallResult`.
2. Create `prompt_builder.py` with versioned canonical prompt envelope.
3. Create `parity.py` with `ParityFingerprint` and mismatch rejection.
4. Update `NaiveRunner` and `GraphGuidedRunner` to delegate to `InstrumentedCallService`.
5. Preserve existing retry/state/observability semantics.

**Tests required**:
- Parity fingerprint matches for identical configuration.
- Fingerprint mismatch raises `ParityMismatchError` before any provider call.
- `InstrumentedCallResult` always contains all three fields.
- Both runners produce structurally identical `RunMetrics` for identical provider responses.

**Definition of Done** (T5.03 is Done only when):
- [ ] Both modes use the same call, prompt-envelope, telemetry, tracing, budget, parser, correctness, and artifact paths.
- [ ] Context acquisition is the only intentional treatment.
- [ ] Parity fingerprint mismatches fail before provider calls.
- [ ] Provider failures are represented identically.
- [ ] Parity tests verify both structural and runtime delegation.
- [ ] Existing retry/state/observability semantics remain intact.

**Independent Verification**:

```bash
uv run pytest tests/unit/services/comparison/test_parity.py tests/unit/services/agent tests/unit/services/comparison -v
```

---
