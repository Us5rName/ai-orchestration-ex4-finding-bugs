# 3. Phase 2 — Shared Layer (Contracts)

[← Back to Home](./Home.md)

**Goal**: Define all cross-cutting **contracts** (interfaces + types). Concrete implementations are deferred to the phases where they're consumed.

## Tasks

| Task | Link | Status |
|---|---|---|
| T2.01 — Implement Version Module | See below | ✅ Done |
| T2.02 — Implement Shared Types | See below | ✅ Done |
| T2.03 — Implement Config Manager (Contract) | See below | ✅ Done |
| T2.04 — Implement API Gatekeeper (Contract) | See below | ✅ Done |
| T2.05 — Implement Token Tracker (Contract) | See below | ✅ Done |
| T2.06 — Shared Layer `__init__.py` | See below | ✅ Done |

---

### T2.01 — Implement Version Module

| Attribute | Value |
|---|---|
| **Status** | ✅ Done |
| **Priority** | P0 |
| **PLAN Reference** | [PLAN §3.9 Shared Layer — version.py] |
| **PRD Reference** | [PRD NFR] version 1.00 |
| **Estimate** | 10 min |
| **Actual** | 5 min |

**Definition of Done**:

- [x] `src/ex04/shared/version.py` exports `__version__ = "1.00"`
- [x] Module-level docstring
- [x] Test verifies version string format

**Independent Verification**:

```bash
uv run pytest tests/unit/shared/test_version.py -v
# Expected: 3 tests pass
```

---

### T2.02 — Implement Shared Types

| Attribute | Value |
|---|---|
| **Status** | ✅ Done |
| **Priority** | P0 |
| **PLAN Reference** | [PLAN §3.9 Shared Layer — types.py] |
| **PRD Reference** | [PRD NFR-4] no hardcoding, [PRD §5.6 FR-6] token metrics |
| **Estimate** | 30 min |
| **Actual** | 20 min |

**Definition of Done**:

- [x] `src/ex04/shared/types.py` — `Entity`, `Relationship`, `Community`, `GraphData`
- [x] `src/ex04/shared/types_metrics.py` — `TokenMetrics`, `RunMetrics`, `ComparisonMetrics`, `ComparisonReport`
- [x] `src/ex04/shared/types_results.py` — `ProviderResponse`, `Suspect`, `InvestigationResult`, `PipelineResult`
- [x] All types use `dataclass` with type hints
- [x] Module-level docstrings
- [x] Tests verify type construction and field presence
- [x] All files ≤ 150 lines ([PRD NFR-3])

**Independent Verification**:

```bash
uv run pytest tests/unit/shared/test_types.py -v --cov=ex04.shared.types --cov-report=term-missing
# Expected: ≥ 85% coverage, all tests pass
```

---

### T2.03 — Implement Config Manager (Contract Only)

| Attribute | Value |
|---|---|
| **Status** | ✅ Done (contract) |
| **Priority** | P0 |
| **PLAN Reference** | [PLAN §3.9 Shared Layer — config.py] |
| **PRD Reference** | [PRD NFR-4] no hardcoding |
| **Estimate** | 45 min |
| **Actual** | 30 min |

**What Phase 2 delivers**: `ConfigManagerInterface` — an ABC with `load()`, `get()`, `validate()` methods.

**Actual implementation**: **Phase 4** — when services need configuration access.

**Definition of Done**:

- [x] `src/ex04/shared/config.py` defines `ConfigManagerInterface` ABC
- [x] `load(path)` → `dict[str, Any]` — loads JSON config
- [x] `get(key_path)` → `Any` — dot-notation access (`provider.name`)
- [x] `validate(config)` → `bool` — checks required fields
- [x] All methods have docstrings with I/O contract
- [x] File ≤ 150 lines
- [x] Tests verify interface contract (abstract, signatures, concrete impl can subclass)

**Independent Verification**:

```bash
uv run pytest tests/unit/shared/test_config.py -v --cov=ex04.shared.config --cov-report=term-missing
# Expected: ≥ 85% coverage, all tests pass
```

---

### T2.04 — Implement API Gatekeeper (Contract Only)

| Attribute | Value |
|---|---|
| **Status** | ✅ Done (contract) |
| **Priority** | P0 |
| **PLAN Reference** | [PLAN §3.9 Shared Layer — gatekeeper.py] |
| **PRD Reference** | [PRD NFR-6] all API calls through gatekeeper |
| **Estimate** | 90 min |
| **Actual** | 45 min |

**What Phase 2 delivers**: `GatekeeperInterface` — an ABC with `send()`, `get_call_log()`, `get_queue_status()` methods.

**Actual implementation**: **Phase 4** — when agent nodes require LLM call routing with rate limiting, FIFO queue, and retry logic.

**Definition of Done**:

- [x] `src/ex04/shared/gatekeeper.py` defines `GatekeeperInterface` ABC
- [x] `send(provider, messages)` → `ProviderResponse` — executes API call
- [x] `get_call_log()` → `list[dict]` — returns call records with timestamps
- [x] `get_queue_status()` → `dict` — returns queue size, processing state, rate limit status
- [x] All methods have docstrings with I/O contract
- [x] File ≤ 150 lines
- [x] Tests verify interface contract

**Features deferred to Phase 4**:

- Rate limiting from `config/rate_limits.json`
- FIFO queue for overflow requests
- Retry logic with configurable attempts/delay
- Call logging with timestamps

**Independent Verification**:

```bash
uv run pytest tests/unit/shared/test_gatekeeper.py -v --cov=ex04.shared.gatekeeper --cov-report=term-missing
# Expected: ≥ 85% coverage
# Tests use mock provider — no real API calls
```

---

### T2.05 — Implement Token Tracker (Contract Only)

| Attribute | Value |
|---|---|
| **Status** | ✅ Done (contract) |
| **Priority** | P1 |
| **PLAN Reference** | [PLAN §3.9 Shared Layer — token_tracker.py] |
| **PRD Reference** | [PRD §5.6 FR-6] token comparison metrics |
| **Estimate** | 45 min |
| **Actual** | 30 min |

**What Phase 2 delivers**: `TokenTrackerInterface` — an ABC with `record()`, `total()`, `by_session()`, `export()` methods.

**Actual implementation**: **Phase 6** — when the comparison service needs to track and compare token usage between naive and graph-guided approaches.

**Definition of Done**:

- [x] `src/ex04/shared/token_tracker.py` defines `TokenTrackerInterface` ABC
- [x] `record(metrics)` → `None` — stores token usage per session
- [x] `total(provider)` → `int` — cumulative tokens by provider
- [x] `by_session(session_id)` → `dict` — session-level metrics
- [x] `export()` → `dict` — serializable dict for reporting
- [x] All methods have docstrings with I/O contract
- [x] File ≤ 150 lines
- [x] Tests verify interface contract

**Features deferred to Phase 6**:

- Thread-safe recording (for parallel comparison runs)
- Cumulative token totals by provider
- Session-level metrics aggregation
- Serializable export for comparison reports

**Independent Verification**:

```bash
uv run pytest tests/unit/shared/test_token_tracker.py -v --cov=ex04.shared.token_tracker --cov-report=term-missing
# Expected: ≥ 85% coverage
```

---

### T2.06 — Shared Layer `__init__.py`

| Attribute | Value |
|---|---|
| **Status** | ✅ Done |
| **Priority** | P0 |
| **PLAN Reference** | [PLAN §3.9 Shared Layer] |
| **Estimate** | 5 min |
| **Actual** | 5 min |

**Definition of Done**:

- [x] `src/ex04/shared/__init__.py` exports all public types and interfaces
- [x] Import verification passes

**Independent Verification**:

```bash
uv run python -c "from ex04.shared import ConfigManagerInterface, GatekeeperInterface, TokenTrackerInterface, TokenMetrics, GraphData; print('OK')"
```

---

## Contract → Implementation Mapping

| Contract (Phase 2) | Actual Implementation | Phase |
|---|---|---|
| `ConfigManagerInterface` | `ConfigManager` (JSON loader) | **Phase 4** (services need config) |
| `GatekeeperInterface` | `APIGatekeeper` (rate limiting, queue, retry) | **Phase 4** (agent nodes call gatekeeper) |
| `TokenTrackerInterface` | `TokenTracker` (thread-safe recording) | **Phase 6** (comparison needs token tracking) |

---

## Validation Summary

| Check | Result |
|---|---|
| Tests pass | ✅ 48/48 |
| Ruff violations | ✅ 0 |
| File ≤ 150 lines | ✅ Max 102 (types.py) |
| Shared layer coverage | ✅ 100% |
| All contracts importable | ✅ |

---

**Source**: Extracted from [`docs/TODO.md`](../TODO.md) §3.
