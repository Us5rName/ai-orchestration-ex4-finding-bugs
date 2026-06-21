# PRD — Reproducible Self-Grade Service

| Field | Value |
|---|---|
| **Requirement ID** | PRD-SG |
| **Parent PRD** | [docs/PRD.md](PRD.md) §5.8 (FR-8.1–FR-8.4) |
| **Status** | Planned |
| **Date** | 2026-06-21 |

---

## Purpose

Define the contract for a reproducible, evidence-derived self-assessment service that
evaluates the repository against a configurable rubric without requiring provider API
credentials. The service produces a canonical JSON report and a Markdown rendering.

---

## Scope

Covers: rubric configuration schema, gate/check configuration schema, typed result
statuses, score calculation, mandatory-gate caps, provenance fields, SDK and CLI
exposure, testing strategy, and security constraints.

Out of scope: LLM provider calls, live investigation runs, comparison token evidence.

---

## Design Rejection

**The following weak design is explicitly rejected:**
A self-grade configuration that contains pre-awarded earned scores. In such a design,
a grade remains high even when mandatory gates fail. This defeats the purpose of
gates and makes the score meaningless.

**Required design:** Configuration contains maximum points and policies only. Earned
scores are computed at run time from actual check results and discovered evidence.

---

## Inputs

| Input | Type | Description |
|---|---|---|
| `rubric_config_path` | `Path` | Path to rubric configuration JSON (max points, policies, gate mapping) |
| `gate_runner` | `GateRunnerInterface` | Injectable executor (subprocess in production, mock in tests) |
| `working_dir` | `Path \| None` | Deterministic working directory (defaults to repository root) |
| `env_overrides` | `dict[str, str] \| None` | Controlled environment variables for reproducibility |

---

## Outputs

| Output | Type | Description |
|---|---|---|
| `GradeReport` | dataclass | Typed grade report with all check results, scores, and provenance |
| `self_grade.json` | file | Canonical machine-readable report |
| `self_grade.md` | file | Markdown rendering derived from `self_grade.json` |

---

## Rubric Configuration Schema

```json
{
    "rubric_version": "1.0.0",
    "sections": [
        {
            "id": "S1",
            "name": "Code Quality",
            "checks": [
                {
                    "id": "S1-C1",
                    "name": "Ruff lint passes",
                    "command": ["uv", "run", "ruff", "check", "."],
                    "max_points": 10,
                    "mandatory": true,
                    "mandatory_cap": 59,
                    "timeout_seconds": 60,
                    "pass_on_exit_code": 0
                }
            ]
        }
    ]
}
```

**Rules:**
- Configuration defines `max_points` and policies only.
- Configuration must NOT contain `earned_points` or `awarded_points` fields.
- `mandatory: true` checks trigger a score cap when they fail.
- `mandatory_cap` defines the maximum final score when this gate fails.
- Multiple failing mandatory gates apply the lowest cap.

---

## Gate/Check Configuration Schema

Each check has:

| Field | Type | Description |
|---|---|---|
| `id` | str | Stable unique check identifier |
| `name` | str | Human-readable check name |
| `command` | list[str] | Command to execute via gate runner |
| `max_points` | float | Maximum points if check passes |
| `mandatory` | bool | Whether failure triggers a score cap |
| `mandatory_cap` | float \| null | Final score cap when this mandatory gate fails |
| `timeout_seconds` | int | Seconds before check is marked TIMEOUT |
| `pass_on_exit_code` | int | Exit code that counts as PASS (default 0) |
| `required` | bool | Whether SKIPPED counts as partial credit or zero |

---

## Typed Result Statuses

| Status | Meaning |
|---|---|
| `PASS` | Check executed and met pass condition |
| `FAIL` | Check executed and did not meet pass condition |
| `ERROR` | Infrastructure or execution error (not a check failure) |
| `SKIPPED` | Check was not run due to missing prerequisite or config |
| `BLOCKED` | Check cannot run because a prerequisite gate failed |

**Distinction:** `FAIL` means the check ran and the code or evidence did not meet the
standard. `ERROR` means the service could not execute the check at all (command not
found, permission denied, unexpected exception). These must not be conflated.

---

## Score Calculation

```
check results
    ↓
earned rubric points  (from PASS results only; FAIL/ERROR/SKIPPED → 0 for that check)
    ↓
raw score             (sum of earned points / sum of max points × 100)
    ↓
mandatory-gate cap    (if any mandatory gate is FAIL, cap raw score at mandatory_cap)
    ↓
final score           (min(raw_score, mandatory_cap) — or raw_score if no gate failed)
```

**Example (illustrative policy documentation, not generated evidence):**

```
Raw rubric score: 94
Correctness gate: FAIL
Mandatory cap: 59
Final score: 59
```

---

## Behavior Table

| Condition | Behavior |
|---|---|
| Check passes | Status=PASS; earned points = max_points |
| Check fails | Status=FAIL; earned points = 0 |
| Command not found | Status=ERROR; earned points = 0; error message captured |
| Timeout exceeded | Status=ERROR; earned points = 0; duration recorded |
| Mandatory gate fails | Apply mandatory_cap to final score |
| Multiple mandatory gates fail | Apply lowest mandatory_cap |
| BLOCKED check | Status=BLOCKED; earned points = 0; blocking gate ID recorded |
| SKIPPED check (required=True) | Counts as FAIL for scoring |
| SKIPPED check (required=False) | Omitted from score denominator |

---

## Required Provenance Fields

Every `self_grade.json` must contain:

| Field | Type | Description |
|---|---|---|
| `grade_id` | str | UUID or timestamp-based unique ID |
| `timestamp` | str (ISO-8601) | When the grade run started |
| `commit_sha` | str | HEAD commit SHA at grade time |
| `dirty_worktree` | bool | Whether the working tree had uncommitted changes |
| `rubric_version` | str | Version from rubric configuration |
| `config_hash` | str | SHA-256 of the full rubric configuration |
| `tool_versions` | dict[str, str] | Versions of ruff, mypy, pytest, uv, python used |
| `commands_executed` | list[dict] | Per-check: command, exit_code, duration_seconds |
| `durations_seconds` | dict[str, float] | Per-check wall-clock durations |
| `timestamps` | dict[str, str] | Per-check start timestamps |
| `evidence_paths` | list[str] | Paths to evidence files referenced in scoring |
| `check_results` | list[CheckResult] | Full typed results per check |
| `raw_score` | float | Pre-cap score |
| `mandatory_caps_applied` | list[dict] | Which caps were applied and why |
| `final_score` | float | Post-cap score |

---

## SDK and CLI Exposure

**SDK (planned):**
```python
Ex04SDK.self_grade(
    rubric_config_path: Path,
    output_dir: Path,
    gate_runner: GateRunnerInterface | None = None,
    working_dir: Path | None = None,
) -> GradeReport
```

**CLI (optional thin wrapper):**
```bash
python -m ex04 self-grade [--rubric config/self_grade_rubric.json] [--output-dir artifacts/self_grade/]
```

The CLI must delegate entirely to the SDK. No grading logic in the CLI.

---

## Testing Strategy

| Test Type | Coverage |
|---|---|
| Unit: grade math | Verify raw score, cap application, final score for various check result combinations |
| Unit: gate runner injection | Verify subprocess runner vs. mock runner produce identical `GradeReport` shape |
| Unit: FAIL/ERROR distinction | Verify command-not-found → ERROR, test failure → FAIL |
| Unit: mandatory cap | Verify cap is applied correctly; multiple caps select lowest |
| Unit: timeout | Verify timeout → ERROR status, duration recorded |
| Unit: BLOCKED | Verify BLOCKED propagation when prerequisite gate fails |
| Unit: provenance | Verify all required provenance fields present and non-empty |
| Unit: JSON → Markdown | Verify Markdown is derived from JSON, not independently authored |
| Integration: real checks | Run ruff and file-length checks against test fixtures |

---

## Acceptance Criteria

- [ ] `GradeReport` contains all required provenance fields.
- [ ] Score calculation follows: check results → earned points → raw score → mandatory cap → final score.
- [ ] Configuration never contains pre-awarded earned scores.
- [ ] Mandatory gate failure reduces final score to cap.
- [ ] `FAIL` and `ERROR` statuses are distinct and separately counted.
- [ ] `BLOCKED` status propagates when a prerequisite gate fails.
- [ ] `self_grade.json` is the canonical report; `self_grade.md` is derived from it.
- [ ] Gate runner is injectable (subprocess runner in production, mock in tests).
- [ ] Unit tests cover all status types, gate math, timeouts, and missing commands.
- [ ] SDK method `Ex04SDK.self_grade()` exists and delegates to the service.
- [ ] Service runs without provider API credentials (keyless).

---

## Security Constraints

- No API keys or provider credentials in grade reports.
- Stdout/stderr captured from checks must be bounded (max length configurable).
- Absolute machine paths stripped from all report outputs.
- Working directory is controlled and deterministic; checks may not modify the repository.
- Commands are validated against a whitelist before execution (no shell injection).

---

## Revision History

| Version | Date | Change |
|---|---|---|
| 1.0 | 2026-06-21 | Initial creation defining self-grade contract for T8.13. Traceability: [PRD §5.8 FR-8.1–FR-8.4], [TODO T8.13], [PLAN §3.10]. |
