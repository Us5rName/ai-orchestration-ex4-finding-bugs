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

## Revision History

| Version | Date | Change |
|---|---|---|
| 1.00 | 2026-06-19 | Initial prompt log — SDLC documentation phase |
