<!-- GENERATED FROM CANONICAL DOCUMENTATION - DO NOT EDIT DIRECTLY -->

# 3. Phase 2 — Shared Layer

[Back to Home](./Home.md)

**Goal**: Implement all cross-cutting infrastructure. Fully testable without any other module.

### T2.01 — Implement Version Module

| Attribute | Value |
|---|---|
| **Status** | Done |
| **Priority** | P0 |
| **PLAN Reference** | [PLAN §3.9 Shared Layer — version.py] |
| **PRD Reference** | [PRD NFR] version 1.00 |
| **Estimate** | 10 min |

**Definition of Done**:

- [ ] `src/ex04/shared/version.py` exports `__version__ = "1.00"`
- [ ] Module-level docstring
- [ ] Test verifies version string format

**Independent Verification**:

```bash
uv run pytest tests/unit/shared/test_version.py -v
# Expected: 1 test passes
```

---

### T2.02 — Implement Shared Types

| Attribute | Value |
|---|---|
| **Status** | Done |
| **Priority** | P0 |
| **PLAN Reference** | [PLAN §3.9 Shared Layer — types.py] |
| **PRD Reference** | [PRD NFR-4] no hardcoding, [PRD §5.6 FR-6] token metrics |
| **Estimate** | 30 min |

**Definition of Done**:

- [ ] `src/ex04/shared/types.py` defines all shared data classes and TypedDicts:
  - `TokenMetrics` with `input_tokens`, `output_tokens`, `total_tokens`, `provider`, `model`
  - `GraphData` with `entities`, `relationships`, `communities`
  - `RunMetrics` with `tokens_used`, `files_read`, `iterations`, `time_seconds`, `found_root_cause`
  - `ComparisonMetrics` with `naive`, `guided`, `token_savings_pct`, `file_read_savings_pct`, `iteration_savings_pct`
  - `PipelineResult` with `graph_result`, `vault_result`, `investigation`, `comparison`, `engineering`
  - `ProviderResponse` with `text`, `input_tokens`, `output_tokens`, `model`, `provider`, `timestamp`
- [ ] All types use `dataclass` or `TypedDict` with type hints
- [ ] Module-level docstring
- [ ] Tests verify type construction and field presence
- [ ] File ≤ 150 lines ([PRD NFR-3])

**Independent Verification**:

```bash
uv run pytest tests/unit/shared/test_types.py -v --cov=ex04.shared.types --cov-report=term-missing
# Expected: ≥ 85% coverage, all tests pass
```

---

### T2.03 — Implement Config Manager

| Attribute | Value |
|---|---|
| **Status** | Done |
| **Priority** | P0 |
| **PLAN Reference** | [PLAN §3.9 Shared Layer — config.py] |
| **PRD Reference** | [PRD NFR-4] no hardcoding |
| **Estimate** | 45 min |

**Definition of Done**:

- [ ] `ConfigManager.load(path)` reads JSON and returns validated `Config` object
- [ ] `ConfigManager.get(key_path)` supports dot-notation access (`provider.name`)
- [ ] `ConfigManager.validate(config)` checks required fields
- [ ] Handles missing file, invalid JSON, missing required fields with clear errors
- [ ] All methods have docstrings with I/O contract
- [ ] File ≤ 150 lines ([PRD NFR-3])

**Independent Verification**:

```bash
uv run pytest tests/unit/shared/test_config.py -v --cov=ex04.shared.config --cov-report=term-missing
# Expected: ≥ 85% coverage, all tests pass
```

---

### T2.04 — Implement API Gatekeeper

| Attribute | Value |
|---|---|
| **Status** | Done |
| **Priority** | P0 |
| **PLAN Reference** | [PLAN §3.9 Shared Layer — gatekeeper.py] |
| **PRD Reference** | [PRD NFR-6] all API calls through gatekeeper |
| **Estimate** | 90 min |

**Definition of Done**:

- [ ] `APIGatekeeper.send(provider, messages)` executes call through provider and returns `ProviderResponse`
- [ ] Rate limiting enforced from `config/rate_limits.json`
- [ ] FIFO queue for overflow requests — never crash on rate limit
- [ ] Call log with timestamps available via `get_call_log()`
- [ ] Queue status available via `get_queue_status()`
- [ ] Retry logic with configurable attempts and delay
- [ ] All methods have docstrings with I/O contract
- [ ] File ≤ 150 lines — split queue logic to `queue.py` if needed

**Independent Verification**:

```bash
uv run pytest tests/unit/shared/test_gatekeeper.py -v --cov=ex04.shared.gatekeeper --cov-report=term-missing
# Expected: ≥ 85% coverage
# Tests use MockProvider — no real API calls
```

---

### T2.05 — Implement Token Tracker

| Attribute | Value |
|---|---|
| **Status** | Done |
| **Priority** | P1 |
| **PLAN Reference** | [PLAN §3.9 Shared Layer — token_tracker.py] |
| **PRD Reference** | [PRD §5.6 FR-6] token comparison metrics |
| **Estimate** | 45 min |

**Definition of Done**:

- [ ] `TokenTracker.record(metrics)` stores token usage per session
- [ ] `TokenTracker.total(provider)` returns cumulative tokens by provider
- [ ] `TokenTracker.by_session(session_id)` returns session-level metrics
- [ ] `TokenTracker.export()` returns serializable dict
- [ ] Thread-safe implementation (for parallel comparison runs)
- [ ] All methods have docstrings with I/O contract

**Independent Verification**:

```bash
uv run pytest tests/unit/shared/test_token_tracker.py -v --cov=ex04.shared.token_tracker --cov-report=term-missing
# Expected: ≥ 85% coverage
```

---

### T2.06 — Shared Layer `__init__.py`

| Attribute | Value |
|---|---|
| **Status** | Done |
| **Priority** | P0 |
| **PLAN Reference** | [PLAN §3.9 Shared Layer] |
| **Estimate** | 5 min |

**Definition of Done**:

- [ ] `src/ex04/shared/__init__.py` exports all public types and classes
- [ ] Import verification passes

**Independent Verification**:

```bash
uv run python -c "from ex04.shared import APIGatekeeper, ConfigManager, TokenTracker, TokenMetrics, GraphData; print('OK')"
```

---
