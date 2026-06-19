# 7. Phase 6 — Comparison Service

[← Back to Home](./Home.md)

**Goal**: Implement token comparison (naive vs. graph-guided).

## Tasks

| Task | Link |
|---|---|
| T6.01 — Naive Runner | See below |
| T6.02 — Graph-Guided Runner | See below |
| T6.03 — Metrics Calculator | See below |
| T6.04 — Comparison Report Generator | See below |

---

### T6.01 — Naive Runner

| Attribute | Value |
|---|---|
| **Status** | Not Started |
| **Priority** | P0 |
| **PLAN Reference** | [PLAN §3.7 Comparison Service — naive_runner.py] |
| **PRD Reference** | [PRD FR-6.1] |
| **Estimate** | 60 min |

**Definition of Done**:

- [ ] `NaiveRunner.run(bug_report, source_files)` dumps all code context
- [ ] Makes LLM calls via Gatekeeper without graph guidance
- [ ] Tracks: tokens used, files read, iterations, time elapsed
- [ ] Returns `RunMetrics`

**Independent Verification**:

```bash
uv run pytest tests/unit/services/comparison/test_naive_runner.py -v
# Uses mock provider — no real API calls
```

---

### T6.02 — Graph-Guided Runner

| Attribute | Value |
|---|---|
| **Status** | Not Started |
| **Priority** | P0 |
| **PLAN Reference** | [PLAN §3.7 Comparison Service — graph_guided_runner.py] |
| **PRD Reference** | [PRD FR-6.2] |
| **Estimate** | 60 min |

**Definition of Done**:

- [ ] `GraphGuidedRunner.run(bug_report, graph, vault)` navigates via graph + vault first
- [ ] Makes focused LLM calls via Gatekeeper
- [ ] Tracks: tokens used, files read, iterations, time elapsed
- [ ] Returns `RunMetrics`

**Independent Verification**:

```bash
uv run pytest tests/unit/services/comparison/test_graph_guided_runner.py -v
# Uses mock provider — no real API calls
```

---

### T6.03 — Metrics Calculator

| Attribute | Value |
|---|---|
| **Status** | Not Started |
| **Priority** | P0 |
| **PLAN Reference** | [PLAN §3.7 Comparison Service — metrics.py] |
| **PRD Reference** | [PRD FR-6.3] |
| **Estimate** | 30 min |

**Definition of Done**:

- [ ] `compare(naive, guided)` calculates savings percentages
- [ ] Computes: `token_savings_pct`, `file_read_savings_pct`, `iteration_savings_pct`
- [ ] Returns `ComparisonMetrics`
- [ ] Handles edge cases: zero tokens, equal runs

**Independent Verification**:

```bash
uv run pytest tests/unit/services/comparison/test_metrics.py -v
```

---

### T6.04 — Comparison Report Generator

| Attribute | Value |
|---|---|
| **Status** | Not Started |
| **Priority** | P1 |
| **PLAN Reference** | [PLAN §3.7 Comparison Service — report_gen.py] |
| **PRD Reference** | [PRD FR-6.3] |
| **Estimate** | 30 min |

**Definition of Done**:

- [ ] `generate(metrics)` produces Markdown comparison report
- [ ] Includes side-by-side table of naive vs. guided metrics
- [ ] Includes savings percentages
- [ ] Saves to `reports/` directory

**Independent Verification**:

```bash
uv run pytest tests/unit/services/comparison/test_report_gen.py -v
```

---

**Source**: Extracted from [`docs/TODO.md`](../TODO.md) §7.
