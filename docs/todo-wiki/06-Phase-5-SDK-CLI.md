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
| **Status** | Not Started |
| **Priority** | P0 |
| **PLAN Reference** | [PLAN §3.2 SDK Module] |
| **PRD Reference** | [PRD NFR-5] SDK-first |
| **Estimate** | 60 min |

**Definition of Done**:

- [ ] `Ex04SDK.from_config(config_path)` creates SDK with all services
- [ ] `run_graphify(target_path)` delegates to Graph Service
- [ ] `build_vault(graph)` delegates to Vault Service
- [ ] `investigate_bug(bug_report)` delegates to Agent Service
- [ ] `run_comparison(bug_report)` delegates to Comparison Service
- [ ] `reverse_engineer(target_path)` delegates to Analysis Service
- [ ] `full_pipeline(target_path, bug_report)` executes complete flow
- [ ] All methods have docstrings
- [ ] File ≤ 150 lines — extract helper methods if needed

**Independent Verification**:

```bash
uv run pytest tests/unit/sdk/test_sdk.py -v --cov=ex04.sdk.sdk --cov-report=term-missing
# Tests with all services mocked
```

---

### T5.02 — Implement CLI Entry Point

| Attribute | Value |
|---|---|
| **Status** | Not Started |
| **Priority** | P1 |
| **PLAN Reference** | [PLAN §1.2 High-Level Architecture — CLI] |
| **Estimate** | 30 min |

**Definition of Done**:

- [ ] CLI accepts commands: `graphify`, `investigate`, `compare`, `pipeline`
- [ ] CLI loads config from `config/setup.json` (or `--config` flag)
- [ ] CLI delegates all logic to SDK — no business logic in CLI
- [ ] Proper error handling and logging

**Independent Verification**:

```bash
uv run python -m ex04 --help
# Should display available commands
```

---

**Source**: Extracted from [`docs/TODO.md`](../TODO.md) §6.
