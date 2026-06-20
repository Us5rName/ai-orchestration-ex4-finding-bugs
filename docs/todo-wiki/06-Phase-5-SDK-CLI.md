# 6. Phase 5 — SDK + CLI

[← Back to Home](./Home.md)

**Goal**: Wire all services through SDK. Add CLI entry point.

## Tasks

| Task | Link |
|---|---|
| T5.01 — Implement SDK | See below |
| T5.02 — Implement CLI Entry Point | See below |

---

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
uv run pytest tests/unit/sdk/test_sdk.py -v --cov=ex04.sdk.sdk --cov-report=term-missing
# Tests with all services mocked
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

**Source**: Extracted from [`docs/TODO.md`](../TODO.md) §6.
