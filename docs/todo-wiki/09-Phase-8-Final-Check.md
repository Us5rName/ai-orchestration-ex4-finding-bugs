<!-- GENERATED FROM CANONICAL DOCUMENTATION - DO NOT EDIT DIRECTLY -->

# 9. Phase 8 — Final Check

[Back to Home](./Home.md)

**Goal**: Verify submission readiness.

### T8.01 — Run Full Test Suite

| Attribute | Value |
|---|---|
| **Status** | Done |
| **Priority** | P0 |
| **PRD Reference** | [PRD KPI: ≥ 85% coverage] |
| **Estimate** | 15 min |

**Definition of Done**:

- [ ] `uv run pytest` passes with 0 failures
- [ ] Coverage ≥ 85% (statement, branch, critical path)
- [ ] Coverage report generated

**Independent Verification**:

```bash
uv run pytest --cov=ex04 --cov-report=term-missing --cov-report=html:coverage_html
```

---

### T8.02 — Run Ruff Lint Check

| Attribute | Value |
|---|---|
| **Status** | Done |
| **Priority** | P0 |
| **PRD Reference** | [PRD NFR-2] zero Ruff violations |
| **Estimate** | 5 min |

**Definition of Done**:

- [ ] `uv run ruff check` returns 0 violations

**Independent Verification**:

```bash
uv run ruff check .
```

---

### T8.03 — Verify File Length Limits

| Attribute | Value |
|---|---|
| **Status** | Done |
| **Priority** | P0 |
| **PRD Reference** | [PRD NFR-3] no file > 150 lines |
| **Estimate** | 5 min |

**Independent Verification**:

```bash
find src -name "*.py" -exec wc -l {} \; | awk '$1 > 150 {print}'
# Should output nothing (all files ≤ 150 lines)
```

---

### T8.04 — Update README.md

| Attribute | Value |
|---|---|
| **Status** | Done |
| **Priority** | P0 |
| **PRD Reference** | [PRD §8 README Requirements] |
| **Estimate** | 60 min |

**Definition of Done**:

- [ ] Repository chosen and rationale documented
- [ ] Bug/problem description
- [ ] Research questions answered
- [ ] Architecture overview
- [ ] Agent workflow description
- [ ] Grphify + Obsidian usage explained
- [ ] Reverse engineering documented
- [ ] Bug, root cause, and fix described
- [ ] Before/after comparison
- [ ] Token efficiency comparison
- [ ] Extensions documented
- [ ] Run instructions
- [ ] Visual elements: screenshots, diagrams, schemas

**Independent Verification**:

```bash
grep -c "##" README.md  # Should have multiple sections
```

---

### T8.05 — Final Checklist

| Attribute | Value |
|---|---|
| **Status** | Done |
| **Priority** | P0 |
| **PRD Reference** | [PRD §12 Final Checklist] |
| **Estimate** | 30 min |

**Definition of Done**:

- [ ] All logic flows through SDK [PRD NFR-5]
- [ ] All API calls flow through Gatekeeper [PRD NFR-6]
- [ ] `ruff check` = 0 violations [PRD NFR-2]
- [ ] Test coverage ≥ 85% [PRD NFR-1]
- [ ] No file > 150 lines [PRD NFR-3]
- [ ] No hardcoded secrets or config [PRD NFR-4]
- [ ] Mandatory docs up to date: PRD, PLAN, TODO
- [ ] `uv` used for all dependency management [PRD NFR-8]
- [ ] README has all HW [§8] requirements
- [ ] All deliverables from [PRD §8] present

---

### T8.06 — CI Workflow

| Attribute | Value |
|---|---|
| **Status** | Done |
| **Priority** | P1 |
| **PRD Reference** | [PRD NFR-7] CI/CD |
| **Estimate** | 30 min |

**Definition of Done**:

- [x] `.github/workflows/ci.yml` runs ruff, mypy, pytest on push and PR
- [x] Coverage gate ≥ 85% enforced in CI

---

### T8.07 — Prompt Registry

| Attribute | Value |
|---|---|
| **Status** | Done |
| **Priority** | P0 |
| **PRD Reference** | [PRD §8 Deliverables] |
| **Estimate** | 60 min |

**Definition of Done**:

- [x] `docs/PROMPTS.md` contains 15 required prompt categories
- [x] Each entry has: ID, title, phase, task, classification, inputs, outputs, constraints
- [x] Traceability table present
- [x] AI-use disclosure updated

---

### T8.08 — Evidence-First README

| Attribute | Value |
|---|---|
| **Status** | Done |
| **Priority** | P0 |
| **PRD Reference** | [PRD §8 README Requirements] |
| **Estimate** | 90 min |

**Definition of Done**:

- [x] README covers all required sections from PRD §8
- [x] Requirement-to-evidence matrix present
- [x] Every factual claim maps to code, test, or committed artifact
- [x] Reproducible self-assessment included

---

### T8.09 — Mechanism PRDs

| Attribute | Value |
|---|---|
| **Status** | Done |
| **Priority** | P1 |
| **PRD Reference** | [PRD §5] |
| **Estimate** | 60 min |

**Definition of Done**:

- [x] `docs/PRD_comparison_experiment.md` created
- [x] `docs/PRD_graph_guided_investigation.md` created
- [x] `docs/PRD_artifact_provenance.md` created
- [x] `docs/PRD_extension_analysis.md` created

---

### T8.10 — Wiki Generation Scripts

| Attribute | Value |
|---|---|
| **Status** | Done |
| **Priority** | P1 |
| **PRD Reference** | [PRD §9 Repository Structure] |
| **Estimate** | 30 min |

**Definition of Done**:

- [x] `scripts/generate_doc_wikis.py` regenerates wiki Home files from canonical docs
- [x] `scripts/check_docs_sync.py` validates sync status
- [x] Scripts are deterministic and idempotent

---

### T8.11 — Validation Scripts

| Attribute | Value |
|---|---|
| **Status** | Done |
| **Priority** | P1 |
| **PRD Reference** | [PRD NFR-2, NFR-3, NFR-4] |
| **Estimate** | 30 min |

**Definition of Done**:

- [x] `scripts/validate_repo.py` checks file sizes, hardcoded values, SDK/gatekeeper boundaries
- [x] Script exits non-zero on violations

---

### T8.12 — Clean-Clone Verification

| Attribute | Value |
|---|---|
| **Status** | Done |
| **Priority** | P0 |
| **PRD Reference** | [PRD §12 Final Checklist] |
| **Estimate** | 20 min |

**Definition of Done**:

- [x] `reports/clean_clone_verification.md` committed with verified results
- [x] Report includes: SHA, Python version, uv version, ruff, mypy, pytest, coverage

---

### T8.13 — Self-Grade Service

| Attribute | Value |
|---|---|
| **Status** | Not Started |
| **Priority** | P0 |
| **Execution Order** | 6th and final of 6 remaining tasks (depends on finalized architecture) |
| **PLAN Reference** | [PLAN §3.10 Self-Grade Service], [PLAN ADR-009] |
| **PRD Reference** | [PRD §5.8 FR-8.1–FR-8.4], [PRD-SG] |
| **Depends On** | All other remaining tasks: T4.19, T5.03, T4.20, T6.05, T6.09 (service grades the finalized architecture) |
| **Estimate** | 90 min |

**Purpose**: Implement a reproducible, evidence-derived self-assessment service. Configuration defines maximum points and policies only — never pre-awarded earned scores. Score is derived from actual check results. Mandatory-gate failures cap the final score.

**T8.13 is implemented last** because its rubric and checks must evaluate the finalized architecture, reports, gates, and evidence — not an intermediate state.

**Planned package**: `src/ex04/services/self_grade/`

```
__init__.py
models.py      — CheckResult, GradeReport, CheckStatus enum (PASS/FAIL/ERROR/SKIPPED/BLOCKED)
config.py      — load and validate rubric configuration (validates no earned_points field)
runner.py      — GateRunnerInterface ABC + SubprocessGateRunner
grader.py      — gate orchestration + evidence-derived score calculation + mandatory cap
renderer.py    — render canonical JSON to Markdown
```

**Score calculation (mandatory)**:
```
check results → earned rubric points → raw score → mandatory-gate cap → final score
```

**Example (illustrative policy, not generated evidence)**:
```
Raw rubric score: 94
Correctness gate: FAIL
Mandatory cap: 59
Final score: 59
```

**Status types**:
| Status | Meaning |
|---|---|
| PASS | Check executed and met pass condition |
| FAIL | Check executed and did not meet pass condition |
| ERROR | Infrastructure/execution error (not a check failure) |
| SKIPPED | Not run due to missing prerequisite |
| BLOCKED | Cannot run because a prerequisite gate failed |

**Required provenance fields in every report**: commit SHA, dirty-worktree state, rubric version, config hash, tool versions, commands executed, durations, timestamps, evidence paths.

**Implementation subtasks**:
1. Create `models.py` with `CheckResult`, `GradeReport`, `CheckStatus`.
2. Create `config.py` to load rubric JSON; validate that no `earned_points` field exists.
3. Create `runner.py` with `GateRunnerInterface` and `SubprocessGateRunner`.
4. Create `grader.py` with score pipeline: results → earned points → raw → cap → final.
5. Create `renderer.py` to render JSON to Markdown.
6. Write `self_grade.json` as canonical; `self_grade.md` derived from it.
7. Add `Ex04SDK.self_grade()`.
8. Add optional thin CLI command (delegates entirely to SDK).

**Tests required** (`tests/unit/services/self_grade/`):
- Grade math: various PASS/FAIL combinations → correct raw score.
- Mandatory cap: gate FAIL → cap applied correctly.
- Multiple gates fail → lowest cap applied.
- FAIL vs. ERROR distinction: command-not-found → ERROR.
- Timeout → ERROR status, duration recorded.
- BLOCKED propagation when prerequisite gate fails.
- All provenance fields present in output.
- JSON canonical; Markdown derived from JSON.
- Injectable gate runner in tests.
- Config validation rejects `earned_points` field.

**Non-goals**:
- Do not add business logic to the CLI.
- Do not grade an intermediate architecture state.
- Do not use pre-configured earned scores.

**Definition of Done** (T8.13 is Done only when):
- [ ] Rubric and gates are configuration-driven.
- [ ] Earned scores are derived from check results.
- [ ] Mandatory caps are applied correctly.
- [ ] Timeouts, missing commands, failures, blocked checks, and execution errors are distinct.
- [ ] Gate runner is injectable.
- [ ] JSON is canonical and Markdown is rendered from it.
- [ ] Provenance is complete.
- [ ] SDK exposure exists.
- [ ] Optional CLI remains thin.
- [ ] Unit and integration tests pass.
- [ ] The service grades the finalized repository.

**Independent Verification**:

```bash
uv run pytest tests/unit/services/self_grade tests/unit/sdk/test_sdk.py -v
```

---
