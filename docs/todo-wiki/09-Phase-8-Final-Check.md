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
| **PRD Reference** | [PRD §12 Final Checklist], [PRD NFR-7] |
| **Estimate** | 90 min |

**Goal**: Add a reproducible self-grade service that assembles structural checks, quality gates, and a rubric score into one typed report.

**Definition of Done**:

- [ ] Add `services/self_grade/` with typed check result and grade report models
- [ ] Load rubric and gate commands from configuration
- [ ] Run structural checks without provider credentials
- [ ] Support injectable gate runner for tests and subprocess runner for production
- [ ] Expose `Ex04SDK.self_grade()` and optional CLI command
- [ ] Unit tests cover grade math, passing/failing checks, missing config, and injected gate runner behavior

**Independent Verification**:

```bash
uv run pytest tests/unit/services/self_grade tests/unit/sdk/test_sdk.py -v
```

---
