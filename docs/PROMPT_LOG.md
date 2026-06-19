# Prompt Engineering Log — EX04 [L1-625]
 ## Session 2026-06-19 [L11-137]
  ### Prompt 1 — Create PRD [L13-31]
  ### Prompt 2 — Create PLAN [L31-51]
  ### Prompt 3 — Create TODO [L51-68]
  ### Prompt 4 — Add Table of Contents [L68-83]
  ### Prompt 5 — Configurable Provider URL [L83-101]
  ### Prompt 6 — Parallel Development [L101-137]
 ## Standards Established [L137-486]
  ### Prompt 7 — Turn PLAN into Wiki [L152-169]
  ### Prompt 8 — Rename Wiki, Log Prompts, Commit [L169-184]
  ### Prompt 9 — Turn TODO into Wiki [L184-202]
  ### Prompt 10 — Log Prompts, Commit [L202-215]
  ### Prompt 11 — Enhance CLAUDE.md with Project Context [L215-242]
  ### Prompt 12 — Git Workflow: Branch, Merge, Push [L242-256]
  ### Prompt 13 — Audit PLAN and PRD for Grphify Mistakes [L256-275]
  ### Prompt 14 — Fix PLAN.md Mistakes [L275-292]
  ### Prompt 15 — Update plan-wiki Sections [L292-309]
  ### Prompt 16 — Audit TODO.md for Stale References [L309-327]
  ### Prompt 17 — Update todo-wiki Sections [L327-342]
  ### Prompt 18 — Audit PRD for Grphify Mistakes [L342-358]
  ### Prompt 19 — Sync PLAN and plan-wiki to PRD Changes [L358-374]
  ### Prompt 20 — Sync TODO and todo-wiki to PLAN Changes [L374-387]
  ### Prompt 21 — Git Workflow: Branch, Commit, Merge, Push, Log [L387-413]
  ### Prompt 22 — Implement Phase 1: Foundation [L413-450]
  ### Prompt 23 — Audit Phase 2, Add Missing Types Task, Renumber [L450-486]
 ## Session 2026-06-19 (continued) [L486-616]
  ### Prompt 24 — Implement Phase 2 (Contract-First Approach) [L488-529]
  ### Prompt 25 — Implement Phase 3: Provider Layer [L529-570]
  ### Prompt 26 — Phase 4 Planning: Codebase Assessment, Approach, Gap Analysis [L570-616]
 ## Session 2026-06-19 — Phase 4 Implementation (Partial) [L616-700]
  ### Prompt 27 — Implement Phase 4: Config Manager & Gatekeeper [L618-660]
  ### Prompt 28 — Implement Phase 4: Graph Service [L660-700]
  ### Prompt 29 — Phase 4 Status Update & Next Agent Handoff [L700-720]
  ### Prompt 30 — Audit & Fix Phase 4 [L720-760]
  ### Prompt 31 — Fix Test Hang [L760-780]

---

### Prompt 30 — Audit & Fix Phase 4

**Prompt**: "Read what he did in the journal, and start fixing, dry violations and line lengths semantically, or tests that weren't written well (ignored the API contract)."

**Context**: Audit Phase 4 code for CLAUDE.md violations and fix them.

**Issues found and fixed**:

| Issue | Severity | Fix | Files |
|---|---|---|---|
| Circular import (`gatekeeper` ↔ `providers/factory`) | 🔴 Critical | Lazy import of `ProviderFactory` inside `send()` | `gatekeeper.py` |
| Ruff F401 (3 unused imports) | 🟡 | Removed unused imports | `test_runner.py`, `test_config_impl.py`, `test_gatekeeper_impl.py` |
| Ruff B017 (blind exception assert) | 🟡 | Added `match` parameter to `pytest.raises` | `test_gatekeeper_send.py` |
| Failing GraphRunner test | 🟡 | Pre-create `graph.json` in test fixture | `test_runner.py` |
| `gatekeeper.py` 249 lines (>150) | 🟡 | Extracted `RateLimiter` to separate module | `gatekeeper.py` (147), `rate_limiter.py` (123) |
| `test_types.py` 231 lines (>150) | 🟡 | Split into 3 focused test files | `test_graph_types.py` (74), `test_metrics_types.py` (67), `test_result_types.py` (84) |
| `test_config_impl.py` 207 lines (>150) | 🟡 | Split into 3 focused test files | `test_config_load.py` (56), `test_config_get.py` (91), `test_config_validate.py` (57) |
| `test_gatekeeper_impl.py` 205 lines (>150) | 🟡 | Split into 2 focused test files | `test_gatekeeper_load.py` (72), `test_gatekeeper_send.py` (148) |
| `test_mocks.py` 154 lines (>150) | 🟡 | Split into 3 focused test files | `test_mock_graph_vault.py` (69), `test_mock_agent_analysis.py` (45), `test_mock_comparison_provider.py` (51) |
| Hardcoded model in gatekeeper | 🟡 | Made `default_model` configurable via constructor | `gatekeeper.py` |
| Tests access internal `_rate_limits` | 🟡 | Updated to use `_limiter.get_config()` | `test_gatekeeper_load.py` |

**Validation results**:
- `uv run ruff check src/ tests/` → 0 violations ✅
- `uv run pytest` → 130 passed ✅
- Coverage: 98.35% (required ≥85%) ✅
- All files ≤150 lines ✅

---

### Prompt 31 — Fix Test Hang

**Prompt**: "I see that each time the tests run they hang for a few seconds. what is the reason?"

**Root cause**: `ApiGatekeeper.send()` calls `time.sleep(retry_delay)` between retry attempts. The default `retry_delay_seconds` is **5 seconds** with **3 retry attempts**, so `test_send_handles_provider_error` slept ~10 seconds before the exception propagated.

**Fix**: Changed `tests/unit/shared/test_gatekeeper_send.py` to use a temp rate-limits config with `retry_delay_seconds: 1` instead of the default 5. Also changed from `0` → `1` per user request (`0` is ambiguous — can mean "never").

**Before**: `rate_limits_path=""` (default 5s delay) → tests hang ~10s
**After**: `rate_limits_path=_fast_retry_path()` (1s delay) → tests complete ~3s

**Validation**: 130 passed in 3.16s, coverage 98.35%.

---

## Revision History

### Prompt 27 — Implement Phase 4: Config Manager & Gatekeeper

**Prompt**: "Switch to a new branch and implement phase 4"

**Context**: Phase 4 — Services. Implement all domain services and shared layer contracts.

**Implementation details**:

| Task | Status | Files | Tests | Notes |
|---|---|---|---|---|
| **T4.00** — ConfigManager | ✅ Done | `src/ex04/shared/config.py` | 15/15 passed | Replaced ABC with concrete impl. `load()`, `get()`, `validate()`. File: 126 lines (<150). |
| **T4.002** — ApiGatekeeper | ✅ Done | `src/ex04/shared/gatekeeper.py` | 13/13 passed | Rate limiting, FIFO queue, retry logic, call logging. File: ~180 lines (exceeds 150 — needs fix). |
| **T4.01** — GraphRunner | ✅ Done | `src/ex04/services/graph/runner.py` | 4/5 passed | Subprocess execution. 1 test failing (see below). |
| **T4.02** — GraphParser | ✅ Done | `src/ex04/services/graph/parser.py` | 7/7 passed | Parses graph.json → GraphData. |
| **T4.03** — GraphAnalyzer | ✅ Done | `src/ex04/services/graph/analyzer.py` | 6/6 passed | God nodes, centrality, communities. |
| **T4.04–T4.06** — Vault Service | 🔶 Not started | — | — | Next tasks. |
| **T4.16–T4.18** — Analysis Service | 🔶 Not started | — | — | Next tasks. |
| **T4.07–T4.15** — Agent Service | 🔶 Not started | — | — | Last (depends on Graph + Vault + Gatekeeper). |

**Validation**:
- `uv run ruff check` — 0 violations on modified files
- ConfigManager: 15/15 tests pass, 98% module coverage
- Gatekeeper: 13/13 tests pass
- GraphService: 17/18 tests pass (1 runner test failing)

**Issues encountered**:
1. Circular import in config.py — fixed by putting both interface and impl in same file
2. Gatekeeper file exceeds 150 lines — needs refactoring (extract helper methods or split)
3. GraphRunner `test_execute_creates_output_dir` — failing because runner checks graph.json exists after subprocess.run, but mock doesn't create it. Fix needed: create graph.json in test before calling execute().

---

### Prompt 28 — Implement Phase 4: Graph Service

**Prompt**: Continue Phase 4 with Graph Service

**Implementation details**:

| Task | Status | Files | Tests | Notes |
|---|---|---|---|---|
| **T4.01** — GraphRunner | ✅ Done | `src/ex04/services/graph/runner.py` | 4/5 passed | Subprocess execution via `graphify` CLI. |
| **T4.02** — GraphParser | ✅ Done | `src/ex04/services/graph/parser.py` | 7/7 passed | Parses nodes→Entity, edges→Relationship, communities→Community. |
| **T4.03** — GraphAnalyzer | ✅ Done | `src/ex04/services/graph/analyzer.py` | 6/6 passed | BFS community detection, degree centrality ranking. |

**Test approach**: Used temp directories with mock JSON files — simple and realistic. Only needed `@patch("subprocess.run")` for runner tests.

---

### Prompt 29 — Phase 4 Status Update & Next Agent Handoff

**Status**: Phase 4 partially complete. Next agent should continue from here.

**Current branch**: `phase4-services`

**Completed tasks**:
- ✅ T4.00 — ConfigManager (15/15 tests)
- ✅ T4.002 — ApiGatekeeper (13/13 tests)
- ✅ T4.01 — GraphRunner (4/5 tests — 1 fix needed)
- ✅ T4.02 — GraphParser (7/7 tests)
- ✅ T4.03 — GraphAnalyzer (6/6 tests)

**Remaining tasks** (in priority order):
1. Fix GraphRunner test: `test_execute_creates_output_dir` — create graph.json in test before calling execute()
2. Fix Gatekeeper file: exceeds 150 lines — extract helper methods or split
3. **T4.04–T4.06** — Vault Service (builder, navigator, note_manager)
4. **T4.16–T4.18** — Analysis Service (reverse_engineer, diagram_gen, bug_report)
5. **T4.07–T4.15** — Agent Service (state, workflow, 7 nodes)

**Key patterns to follow**:
- TDD: write tests first (RED), implement (GREEN), verify
- Temp directories with mock JSON for filesystem tests
- Only patch `subprocess.run` for subprocess-based tests
- Keep files ≤150 lines
- Zero ruff violations
- All config from JSON files, nothing hardcoded

**Files created for test directories** (empty, need content):
- `tests/unit/services/vault/` — needs test files
- `tests/unit/services/analysis/` — needs test files
- `tests/unit/services/agent/nodes/` — needs test files

**Interface contracts already defined** (Phase 2):
- `src/ex04/services/graph/interface.py` — GraphServiceInterface
- `src/ex04/services/vault/interface.py` — VaultServiceInterface
- `src/ex04/services/agent/interface.py` — AgentServiceInterface
- `src/ex04/services/analysis/interface.py` — AnalysisServiceInterface

**Existing stub files** (need implementation):
- `src/ex04/services/vault/builder.py`
- `src/ex04/services/vault/navigator.py`
- `src/ex04/services/vault/note_manager.py`
- `src/ex04/services/analysis/reverse_engineer.py`
- `src/ex04/services/analysis/diagram_gen.py`
- `src/ex04/services/analysis/bug_report.py`
- `src/ex04/services/agent/state.py`
- `src/ex04/services/agent/workflow.py`
- `src/ex04/services/agent/nodes/knowledge.py`
- `src/ex04/services/agent/nodes/analysis.py`
- `src/ex04/services/agent/nodes/suspect.py`
- `src/ex04/services/agent/nodes/inspect.py`
- `src/ex04/services/agent/nodes/rootcause.py`
- `src/ex04/services/agent/nodes/fix.py`
- `src/ex04/services/agent/nodes/verify.py`

---

## Revision History

| Version | Date | Change |
|---|---|---|
| 1.00 | 2026-06-19 | Initial prompt log — SDLC documentation phase |
| 1.01 | 2026-06-19 | Added Prompt 23 — Phase 2 audit, added T2.02 Shared Types task, renumbered Phase 2 tasks |
| 1.02 | 2026-06-19 | Added Prompt 24 — Phase 2 contract-first implementation, documentation updates, and git commits to phase2 branch (4 commits) |
| 1.03 | 2026-06-19 | Added Prompt 25 — Phase 3 provider layer implementation, ProviderResponse contract update, 21 new provider tests |
| 1.04 | 2026-06-19 | Added Prompt 26 — Phase 4 planning: codebase state assessment, approach discussion, gap analysis, documentation updates, branch creation |
| 1.05 | 2026-06-19 | Added Prompt 27 — Phase 4 partial implementation: ConfigManager, Gatekeeper, Graph Service (runner/parser/analyzer). 51/52 tests pass. 1 test fix needed. |
| 1.06 | 2026-06-19 | Added Prompt 30 — Audit and fix Phase 4: circular import, Ruff violations, line counts, failing test, hardcoded values. 130/130 tests pass, 98.35% coverage, 0 Ruff violations, all files ≤150 lines. |
| 1.07 | 2026-06-19 | Added Prompt 31 — Fix test hang: gatekeeper retry sleep (5s default → 1s in tests). Tests complete ~3s instead of hanging. |
