# Prompt Engineering Log — EX04

| Field | Value |
|---|---|
| **Project** | EX04 — Reverse Engineering, Debugging & Token-Efficient Agentic AI |
| **Version** | 1.00 |
| **Date** | 2026-06-19 |

---

## Session 2026-06-19

### Prompt 1 — Create PRD

**Prompt**: "Create a prd for ex04. the PRD must cite the hw. I chose to work with langgraph"

**Context**: Starting SDLC Phase 1 — Requirements. User had `ex04.md` (homework spec) in the project root and needed a formal PRD that cites the homework throughout. User explicitly chose LangGraph (not CrewAI).

**Key decisions captured**:
- PRD cites HW sections using `HW [§X]` format with direct Hebrew quotes from `ex04.md`
- Technology choices table documents LangGraph selection with HW [§6.1] rationale
- Target codebase: `andela/buggy-python` (already cloned in `graph-home`)
- 7 primary goals mapped to HW [§5.1-5.6]
- 36 functional requirements across 7 categories
- 9 non-functional requirements from project standards

**Output**: `docs/PRD.md` v1.00 — 12 sections, all citing HW

---

### Prompt 2 — Create PLAN

**Prompt**: "yes. Make sure to divide to independent modules and to make the project provider agnostic. In the plan, make sure to cite the PRD"

**Context**: SDLC Phase 2 — Architecture. User wanted modular, provider-agnostic design with PRD citations throughout.

**Key decisions captured**:
- 9 independent modules: SDK, Graph, Vault, Agent, Analysis, Comparison, Provider, Shared
- `ProviderInterface` ABC — no hardcoded vendor coupling
- `ProviderFactory` creates providers from config (name + model + base_url + api_key)
- 5 ADRs documenting architectural decisions
- C4 model: Context, Container, Component diagrams
- OOP class diagram with all classes
- Traceability matrix mapping every PRD requirement to a file
- All PRD citations use `[PRD §X.Y]` format

**Output**: `docs/PLAN.md` v1.00 — 12 sections, full C4 model, all citing PRD

---

### Prompt 3 — Create TODO

**Prompt**: "Yes. Make sure you make every step independent - both in implementation and verification. Cite the plan."

**Context**: SDLC Phase 3 — Task Tracking. User needed every task to be independently implementable and verifiable, with PLAN citations.

**Key decisions captured**:
- 40 tasks across 8 phases
- Each task has: Definition of Done, Independent Verification (exact commands), PLAN citation, PRD citation
- Within-phase parallelism: tasks in same phase have zero cross-dependencies
- Between-phase ordering only: Phase 1 → Phase 2 → ... → Phase 8
- Verification commands are copy-paste ready

**Output**: `docs/TODO.md` v1.00 — 40 tasks, all independently verifiable

---

### Prompt 4 — Add Table of Contents

**Prompt**: "Add a table of contents to the PRD, PLAN and TODO in separate files"

**Context**: Usability improvement — all three documents are long; needed quick navigation.

**Changes**:
- Added `## Table of Contents` section to `docs/PRD.md` (12 entries + sub-items)
- Added `## Table of Contents` section to `docs/PLAN.md` (12 entries + sub-items)
- Added `## Table of Contents` section to `docs/TODO.md` (40 tasks listed individually)

**Output**: All three documents updated with internal anchor links

---

### Prompt 5 — Configurable Provider URL

**Prompt**: "can the provider URL be set as well? Cite the docs if you can"

**Context**: User identified gap — `base_url` not configurable. Needed for custom endpoints (Ollama, proxy, local models).

**Answer**: Current design did NOT support configurable URLs. Only `name`, `model`, `api_key_env` in config.

**Changes to PLAN**:
- [PLAN §3.8] Added `base_url: str | None = None` to `ProviderInterface.chat()`
- [PLAN §8.2] Updated API contract to include `base_url` parameter
- [PLAN §9.1] Added `"base_url": null` to config schema
- [PLAN §9.3] Added `OPENAI_BASE_URL` and `ANTHROPIC_BASE_URL` to .env-example

**Output**: PLAN updated — provider URL now fully configurable

---

### Prompt 6 — Parallel Development

**Prompt**: "can every module be run independently of the others? cite the docs in your answer"

Followed by: "The issue I'm trying to solve is to allow parallel development"

**Context**: User identified that the current module dependency graph blocks parallel development — Agent depends on Graph + Vault + Provider, so Agent developer waits for 3 other modules.

**Analysis provided**:
- Shared, Provider, Graph, Vault → can run independently ✅
- Agent, Analysis, Comparison → have cross-dependencies, cannot run independently ❌
- Distinguished between "testable with mocks" vs "executable independently"

**Solution implemented — Contract-First with Interface ABCs**:

Changes to PLAN:
- [PLAN §3] Rewrote module design section — all dependencies flow through `*Interface` ABCs
- [PLAN §3.1] New dependency graph showing interface vs runtime separation
- [PLAN §3.1.1] Service Interfaces table — 6 interfaces defined before implementation
- [PLAN §3.1.2] Parallel development Gantt chart
- [PLAN §3.2] SDK updated to use dependency injection (all services injected via constructor)
- [PLAN §3.3-3.7] Each service now includes `interface.py` as first file
- [ADR-006] New ADR documenting contract-first parallel development decision
- [ADR-007] Renumbered old ADR-005
- [PLAN §10] Project structure updated with all `interface.py` files

Changes to TODO:
- Added T1.05 — Define All Service Interfaces (Contract Layer) — gate for parallel work
- Added T1.06 — Create Mock Implementations for All Services
- Updated Phase 4 goal to emphasize interface-only imports
- Updated statistics (42 tasks, parallel schedule noted)

**Best practice established**: Always define `interface.py` ABC before implementation. Other modules import only the interface. SDK wires concrete implementations at runtime.

---

## Standards Established

| Standard | Description | Document |
|---|---|---|
| **HW Citation Format** | `HW [§X]` with Hebrew quote | PRD |
| **PRD Citation Format** | `[PRD §X.Y]` or `[PRD FR-X.Y]` | PLAN, TODO |
| **PLAN Citation Format** | `[PLAN §X.Y]` or `[ADR-XXX]` | TODO |
| **Task Independence** | Every task has Definition of Done + Independent Verification commands | TODO |
| **Contract-First** | `interface.py` ABC before implementation | PLAN §3, ADR-006 |
| **Provider-Agnostic** | `ProviderInterface` ABC, configurable `base_url` | PLAN §3.8 |
| **150-Line Limit** | No file exceeds 150 lines | PRD NFR-3 |
| **Zero Ruff** | `ruff check` = 0 violations | PRD NFR-2 |

---

### Prompt 7 — Turn PLAN into Wiki

**Prompt**: "The plan is quite large. I want you to turn it into wiki, while not deleting original file. Later, the TODO will also be turned into a wiki"

**Context**: The `docs/PLAN.md` is 1,370 lines — too large for comfortable navigation. User wanted a wiki-style split while preserving the original single-file document.

**Implementation**:
- Created `docs/wiki/` directory (later renamed to `docs/plan-wiki/`)
- Split PLAN into 13 files: `Home.md` index + 12 section pages (`01-Architecture-Overview.md` through `12-Revision-History.md`)
- Each page has **← Home / Prev → Next** navigation links at top and bottom
- All Mermaid diagrams, tables, code blocks, and PRD citations preserved verbatim
- Original `docs/PLAN.md` left untouched

**Output**: `docs/plan-wiki/` — 13 files, fully navigable wiki

---

### Prompt 8 — Rename Wiki, Log Prompts, Commit

**Prompt**: "I changed the name of wiki to plan-wiki. Add the prompts to the prompt log according to the instructions and commit your changes to a new branch in small readable commits"

**Context**: User renamed `docs/wiki/` → `docs/plan-wiki/`. Needed prompt log entries and git commits.

**Changes**:
- Updated `docs/PROMPT_LOG.md` with Prompt 7 and Prompt 8 entries
- Created feature branch `docs/plan-wiki` for commit work
- Committed wiki files and prompt log updates in small, atomic commits

**Best practice established**: Large documentation files should be split into wiki format for navigability while keeping the original as source of record.

---

### Prompt 9 — Turn TODO into Wiki

**Prompt**: "The TODO is quite large. I want you to turn it into wiki, while not deleting original file.\nPlan was already turned into a wiki"

**Context**: The `docs/TODO.md` is 1,577 lines — too large for comfortable navigation. User wanted the same wiki-style split that was already applied to PLAN via `docs/plan-wiki/`.

**Implementation**:
- Created `docs/todo-wiki/` directory following `docs/plan-wiki/` convention
- Split TODO into 13 files: `Home.md` index + 12 section pages (`01-Phase-Overview.md` through `12-Revision-History.md`)
- Each page has **← Back to Home** navigation link at top and source reference at bottom
- All task tables, checkboxes, verification commands, and Mermaid diagrams preserved verbatim
- Phase 4 (Services) grouped by sub-service (Graph, Vault, Agent, Analysis) with task index
- Original `docs/TODO.md` left untouched

**Output**: `docs/todo-wiki/` — 13 files, fully navigable wiki

---

### Prompt 10 — Log Prompts, Commit

**Prompt**: "Add the prompts to the prompt log according to the instructions and commit your changes to a new branch in small readable commits"

**Context**: Wiki files created in Prompt 9 needed prompt log entries and git commits.

**Changes**:
- Updated `docs/PROMPT_LOG.md` with Prompt 9 and Prompt 10 entries
- Created feature branch for commit work
- Committed wiki files and prompt log updates in small, atomic commits

---

### Prompt 11 — Enhance CLAUDE.md with Project Context

**Prompt**: "Do you have suggestion on things to add to claude.md now that the todo and plan wiki and the prd exist?"

**Context**: PRD, PLAN, TODO, plan-wiki, and todo-wiki all existed. `CLAUDE.md` was a generic process/rules document with no project-specific context. An agent reading it wouldn't know what this project actually is.

**Suggestions provided**:
- Add project identity (course, goal, package name, assignment spec reference)
- Add documentation navigation table mapping each doc to purpose and when to consult
- Explicitly direct agents to read wiki versions instead of large PLAN.md/TODO.md
- Add deliverables checklist from assignment spec
- Add project-specific rules (LLM providers, LangGraph, Grphify, comparison methodology)
- Add configuration sources table
- Add error escalation protocol
- Reference traceability matrix

**Changes**:
- Added section `## 0. Project Context` to `CLAUDE.md` with:
  - Project identity (course, goal, package, assignment spec)
  - Documentation Navigation table with wiki-first guidance
  - Explicit rule: "Do not read `docs/PLAN.md` or `docs/TODO.md` directly"
- Existing sections 1–8 left untouched

**Best practice established**: `CLAUDE.md` should be a navigation guide + guardrails, not a duplicate of wiki content. Point to docs, don't repeat them.

---

### Prompt 12 — Git Workflow: Branch, Merge, Push

**Prompt**: "switch to a new branch, and merge. push to origin, merge to master and then push master to origin."

**Context**: Needed to commit CLAUDE.md changes, push feature branch, merge to master, and push master.

**Changes**:
- Committed `CLAUDE.md` on `phase-1-foundation` branch
- Pushed `phase-1-foundation` → `origin/phase-1-foundation`
- Merged `phase-1-foundation` into `master` (fast-forward)
- Pushed `master` → `origin/master`

---

### Prompt 13 — Audit PLAN and PRD for Grphify Mistakes

**Prompt**: "Please read the full plan file (not the wiki) and the full PRD file and tell me if there are any mistakes about it. I meant if graphify usage is correctly mentioned and described."

**Context**: User had access to the Grphify agent skill and wanted to verify that PLAN.md and PRD.md accurately describe Grphify's actual behavior, outputs, and CLI usage.

**Mistakes found**:
1. **ADR-003**: CLI name `graphifyy` (wrong) — actual CLI is `graphify`; `graphifyy` is only the pip package name
2. **ADR-003**: Dismissed library import entirely — Grphify has importable Python API (`from graphify.build import build_from_json`, `graphify query`, etc.)
3. **Config**: `output_dir: "./artifacts"` doesn't map to any real Grphify parameter — Grphify writes to `<scan_root>/graphify-out/`
4. **Missing outputs**: `graph.html`, `.graphify_analysis.json`, `.graphify_labels.json`, `cost.json` not documented
5. **Obsidian ambiguity**: No decision on whether Vault Service uses Grphify's `export obsidian` or builds from scratch
6. **Query capability**: `graphify query/path/explain` not leveraged as potential extension
7. **`--directed` flag**: Not mentioned (preserves edge direction for bug investigation)

**Output**: Detailed audit report with severity ratings for each issue

---

### Prompt 14 — Fix PLAN.md Mistakes

**Prompt**: "Please fix the actual mistakes in the plan. no adr 005 is missing - it's a numbering issue."

**Context**: User confirmed the Grphify audit findings and requested fixes in PLAN.md. Clarified that ADR-005 gap is intentional (numbering issue, not missing content).

**Changes to `docs/PLAN.md`**:
- **ADR numbering**: Renumbered ADR-006→005, ADR-007→006 (sequential 001-006)
- **ADR-003**: Fixed CLI name `graphifyy` → `graphify`. Added hybrid approach: CLI for initial build, library API for investigation. Corrected output path to `graphify-out/graph.json`
- **OOP Schema**: Removed `Ex04SDK --> NaiveRunner` and `Ex04SDK --> GraphGuidedRunner` (SDK must delegate through services). Fixed Gatekeeper direction: `APIGatekeeper --> Provider` (was reversed)
- **SDK Module**: Added missing `full_pipeline()` method signature
- **Shared Types**: Added `PipelineResult` type (was referenced but undefined)
- **Config**: Replaced fictional `output_dir: "./artifacts"` with `output_subdir: "graphify-out"`
- **Traceability Matrix**: Corrected all FR-1.x and FR-2.x mappings to match PRD numbering

---

### Prompt 15 — Update plan-wiki Sections

**Prompt**: "Now update the relevant plan-wiki sections"

**Context**: PLAN.md fixes needed to be mirrored in the corresponding plan-wiki pages.

**Changes**:
| Wiki File | Changes |
|---|---|
| `05-ADRs.md` | ADR-003 content fix, renumbered ADR-006→005, ADR-007→006 |
| `06-OOP-Schema.md` | Fixed SDK direct calls, fixed Gatekeeper direction, added full_pipeline |
| `03-Module-Design.md` | Added full_pipeline(), added PipelineResult type |
| `09-Configuration-Schema.md` | Fixed graphify config |
| `11-Traceability-Matrix.md` | Fixed FR numbering |

---

### Prompt 16 — Audit TODO.md for Stale References

**Prompt**: "is there anything that needs to be updated in the big TODO.md file (not the wiki)?"

**Context**: After fixing PLAN.md, needed to verify TODO.md doesn't have stale references to old ADR numbers, wrong package names, or incorrect paths.

**Issues found and fixed in `docs/TODO.md`**:
| Line | Before | After |
|---|---|---|
| 179 | `graphifyy` (wrong CLI name) | `graphify` |
| 231 | `ADR-006` | `ADR-005` |
| 268 | `ADR-006` | `ADR-005` |
| 559 | `ADR-006` | `ADR-005` |
| 595 | `PRD FR-1.2` (was index.md, not parsing) | `PRD FR-1.1 graph.json parsing` |
| 1212 | `ls -la artifacts/graph.json` | `ls -la graph-home/graphify-out/graph.json` |

---

### Prompt 17 — Update todo-wiki Sections

**Prompt**: "Now update the relevant todo-wiki sections"

**Context**: TODO.md fixes needed to be mirrored in the corresponding todo-wiki pages.

**Changes**:
| Wiki File | Changes |
|---|---|
| `02-Phase-1-Foundation.md` | `graphifyy`→`graphify`, `ADR-006`→`ADR-005` (×2), added `PipelineResult` to types |
| `05-Phase-4-Services.md` | `ADR-006`→`ADR-005`, `FR-1.2`→`FR-1.1` |
| `08-Phase-7-End-to-End.md` | `artifacts/graph.json`→`graph-home/graphify-out/graph.json` (×2) |

---

### Prompt 18 — Audit PRD for Grphify Mistakes

**Prompt**: "is there any mistake in the PRD about the graphify usage?"

**Context**: After fixing PLAN and TODO, needed to check if PRD.md also has Grphify-related inaccuracies.

**Issues found and fixed in `docs/PRD.md`**:
| Location | Before | After |
|---|---|---|
| §1.3 | `graphifyy ≥ 0.8.40` — ambiguous | `graphify` CLI, package: `graphifyy` ≥ 0.8.40 |
| §1.3 rationale | Vague Obsidian claim | Accurate: `graphify-out/graph.json`, `GRAPH_REPORT.md`, HTML, `graphify export obsidian` |
| §9 structure | `artifacts/graph.json` | `graph-home/graphify-out/` with proper subdirectories |
| §9 structure | No `graphify-out/` shown | Added with comment |

---

### Prompt 19 — Sync PLAN and plan-wiki to PRD Changes

**Prompt**: "Now update the plan and then the plan-wiki according to the prd like you did before, if any are needed"

**Context**: PRD changes needed to be synced back to PLAN.md §10 (Project Structure) and plan-wiki.

**Changes to `docs/PLAN.md` §10**:
- `ADR-006` → `ADR-005` (5 occurrences in interface.py comments)
- `FR-1.2` → `FR-1.1` for parser.py comment
- Removed `artifacts/` directory
- Added `graphify-out/` under `graph-home/` with `.graphify/repos/` subdirectories

**Changes to `docs/plan-wiki/10-Project-Structure.md`**: Same changes mirrored

---

### Prompt 20 — Sync TODO and todo-wiki to PLAN Changes

**Prompt**: "Now update the todo and then the todo-wiki according to the plan like you did before, if any are needed"

**Context**: PLAN changes needed to be synced to TODO.md and todo-wiki.

**Changes to `docs/TODO.md`**:
- Line 1204: `graph.json` produced in `artifacts/` → `graph-home/graphify-out/`

**Changes to todo-wiki**: Already clean from Prompt 17 — no additional changes needed.

---

### Prompt 21 — Git Workflow: Branch, Commit, Merge, Push, Log

**Prompt**: "now switch to a new branch, and commit in small readable steps. then merge the branch to master and push master. then write everything you did in the prompt log."

**Context**: All documentation fixes from prompts 13-20 needed to be committed, merged, and pushed.

**Git workflow**:
- Created branch `fix/doc-consistency-pass`
- Committed in 6 logical, atomic commits:

| # | Commit | Files |
|---|---|---|
| 1 | `docs: fix ADR numbering (006→005, 007→006) and ADR-003 Grphify content` | PLAN.md, plan-wiki/05-ADRs.md, TODO.md, todo-wiki/02, todo-wiki/05 |
| 2 | `docs: fix traceability matrix FR numbering` | plan-wiki/11-Traceability-Matrix.md |
| 3 | `docs: fix OOP schema dependency arrows` | plan-wiki/06-OOP-Schema.md |
| 4 | `docs: add full_pipeline() method and PipelineResult type` | plan-wiki/03-Module-Design.md |
| 5 | `docs: fix Grphify output paths and project structure` | plan-wiki/09, plan-wiki/10, todo-wiki/08 |
| 6 | `docs: fix PRD Grphify technology choices and repository structure` | PRD.md |

- Fast-forward merged `fix/doc-consistency-pass` → `master`
- Pushed `master` → `origin/master` (37 objects, 12 files changed, +94/-77 lines)

**Best practice established**: When fixing documentation consistency, commit by theme (not by file) so each commit tells a coherent story. Cross-document changes (PLAN + wiki + TODO) belong in the same commit.

---

### Prompt 22 — Implement Phase 1: Foundation

**Prompt**: "implement phase 1. remember to check the success criteria at the end."

**Context**: Phase 1 (Foundation) establishes project structure, configuration, and tooling — no business logic yet. Six tasks: directory structure, config files, pyproject.toml, base data types, service interfaces, mock implementations.

**Implementation details**:

| Task | Description | Files Created |
|---|---|---|
| T1.01 | Project directory structure + stubs | 51 Python files (src/ex04/…, config/, tests/, obsidian/, graph-home/, reports/) |
| T1.02 | Configuration files | config/setup.json, config/rate_limits.json, .env-example, .gitignore updated |
| T1.03 | pyproject.toml | Updated: ruff config, pytest config (85% coverage), dependencies (langgraph, graphifyy, openai, anthropic, pydantic), hatch build for src layout |
| T1.04 | Base data types | src/ex04/shared/types.py (102 lines), types_metrics.py (81 lines), types_results.py (89 lines) — split to respect 150-line limit |
| T1.05 | Service interfaces | 5 ABCs: GraphServiceInterface, VaultServiceInterface, AgentServiceInterface, AnalysisServiceInterface, ComparisonServiceInterface |
| T1.06 | Mock implementations | 6 mocks + __init__.py + 14 verification tests |

**Validation results**:
- `uv run ruff check .` — 0 violations
- `uv run pytest tests/unit/test_mocks.py -v` — 14/14 passed
- Test coverage — 97.4% (≥85% required)
- File line limits — max 102 lines (all under 150)
- All types importable from `ex04.shared.types`
- All interfaces importable

**Issues encountered and resolved**:
1. `graphify>=0.8.40` not on PyPI — fixed to `graphifyy>=0.8.40` (package name on PyPI is `graphifyy`, import name is `graphify`)
2. `uv sync` failed — resolved by adding `[tool.hatch.build.targets.wheel] packages = ["src/ex04"]` and `uv pip install -e .`
3. `TokenMetrics().model_dump()` failed — dataclass, not Pydantic. Fixed to `asdict(TokenMetrics())`
4. `types.py` was 222 lines (exceeds 150-line limit) — split into types.py, types_metrics.py, types_results.py with re-exports
5. Cross-module type references in types_results.py — added `from ex04.shared.types_metrics import ComparisonReport, TokenMetrics`
6. ProviderFactory.create/register uncovered (78%) — expected, requires Phase 3 provider implementations. Documented in todo-wiki/12-Revision-History.md v1.01.

**Best practice established**: When splitting a large types file to respect the 150-line limit, keep the original import path working via re-exports in the main types.py. This avoids updating every downstream import across interfaces and tests.

---

### Prompt 23 — Audit Phase 2, Add Missing Types Task, Renumber

**Prompt**: "what does phase 2 entail?" → "any other information that you need to get from the plan wiki for the phase?" → "that it's a good idea to put it before the other tasks, because they depend on it. what do you think?" → "please update in the wiki and in the actual file, and fix the numbering"

**Context**: Reviewed Phase 2 (Shared Layer) tasks against PLAN wiki §3.9. Found that `types.py` (6 shared data classes) was defined in the Module Design but had no corresponding task in TODO.md. Additionally `ProviderResponse` from API Contract §8.2 was also missing.

**Findings**:

| Gap | Source | Impact |
|---|---|---|
| `types.py` missing from tasks | PLAN §3.9 | Gatekeeper, TokenTracker have no `TokenMetrics`, `ProviderResponse` to use |
| `ProviderResponse` missing | API Contract §8.2 | Gatekeeper's `send()` has no return type defined |
| Task ordering wrong | Dependency analysis | Types should be T2.02 (before Config, Gatekeeper, TokenTracker) |

**Changes made**:

| File | Change |
|---|---|
| `docs/TODO.md` | Added T2.02 (Shared Types), renumbered T2.02→T2.06, updated TOC, updated mermaid dependency diagram |
| `docs/todo-wiki/03-Phase-2-Shared-Layer.md` | Added T2.02 (Shared Types), renumbered all tasks, updated task table |

**New task order**:

| Task | What | Depends On |
|---|---|---|
| T2.01 | Version Module | — |
| T2.02 | **Shared Types** | — |
| T2.03 | Config Manager | T2.02 |
| T2.04 | API Gatekeeper | T2.02, T2.03 |
| T2.05 | Token Tracker | T2.02 |
| T2.06 | Shared `__init__.py` | all above |

**Best practice established**: Always cross-reference the todo-wiki against the plan-wiki Module Design (§3.x) and API Contract (§8.x) before starting implementation. Missing types/tasks create blockers downstream.

---

## Revision History

| Version | Date | Change |
|---|---|---|
| 1.00 | 2026-06-19 | Initial prompt log — SDLC documentation phase |
| 1.01 | 2026-06-19 | Added Prompt 23 — Phase 2 audit, added T2.02 Shared Types task, renumbered Phase 2 tasks |
