# 9. Phase 8 — Final Check

[← Back to Home](./Home.md)

**Goal**: Verify submission readiness.

## Tasks

| Task | Link |
|---|---|
| T8.01 — Run Full Test Suite | See below |
| T8.02 — Run Ruff Lint Check | See below |
| T8.03 — Verify File Length Limits | See below |
| T8.04 — Update README.md | See below |
| T8.05 — Final Checklist | See below |

---

### T8.01 — Run Full Test Suite

| Attribute | Value |
|---|---|
| **Status** | Not Started |
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
| **Status** | Not Started |
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
| **Status** | Not Started |
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
| **Status** | Not Started |
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
| **Status** | Not Started |
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

**Source**: Extracted from [`docs/TODO.md`](../TODO.md) §9.
