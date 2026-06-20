# 5. Phase 4 — Services

[← Back to Home](./Home.md)

**Goal**: Implement all domain services and shared layer contracts deferred from Phase 2. Each service imports only `*Interface` contracts — never concrete implementations from other services. Real wiring happens through SDK at runtime ([ADR-005]).

## Task Index

| Task | Service | Link |
|---|---|---|
| T4.00–T4.002 | Shared Layer Implementations | See below |
| T4.01–T4.03 | Graph Service | See below |
| T4.04–T4.06 | Vault Service | See below |
| T4.07–T4.15 | Agent Service | See below |
| T4.16–T4.18 | Analysis Service | See below |

---

### Shared Layer Implementations (T4.00–T4.002)

> **Rationale**: `ConfigManagerInterface` and `GatekeeperInterface` were defined as contracts in Phase 2 ([PLAN §3.9]) with "impl in P4" comments. All domain services depend on these. Implemented here as prerequisites before any service work.

#### T4.00 — Config Manager Implementation

| Attribute | Value |
|---|---|
| **Status** | Done |
| **Priority** | P0 |
| **PLAN Reference** | [PLAN §3.9 Shared Layer — config.py] |
| **PRD Reference** | [PRD NFR-4] configuration externalization |
| **Estimate** | 30 min |

**Definition of Done**:

- [ ] `ConfigManager` implements `ConfigManagerInterface`
- [ ] `load(path)` reads JSON config file and caches
- [ ] `get(key_path)` supports dot-notation (e.g. `agent.max_iterations`)
- [ ] `validate(config)` checks required fields
- [ ] No hardcoded config values — all from `config/setup.json`
- [ ] File ≤ 150 lines

**Independent Verification**:

```bash
uv run pytest tests/unit/shared/test_config_impl.py -v --cov=ex04.shared.config --cov-report=term-missing
```

---

#### T4.002 — Gatekeeper Implementation

| Attribute | Value |
|---|---|
| **Status** | Done |
| **Priority** | P0 |
| **PLAN Reference** | [PLAN §3.9 Shared Layer — gatekeeper.py] |
| **PRD Reference** | [PRD NFR-1] API call management |
| **Estimate** | 60 min |

**Definition of Done**:

- [ ] `ApiGatekeeper` implements `GatekeeperInterface`
- [ ] `send(provider, messages)` routes through `ProviderFactory`, enforces rate limits
- [ ] Rate limits loaded from `config/rate_limits.json`
- [ ] FIFO queue for overflow requests
- [ ] Retry logic with configurable attempts/delay
- [ ] `get_call_log()` returns timestamped call records
- [ ] `get_queue_status()` returns queue depth and state
- [ ] All LLM calls in agent nodes flow through gatekeeper
- [ ] File ≤ 150 lines

**Independent Verification**:

```bash
uv run pytest tests/unit/shared/test_gatekeeper_impl.py -v --cov=ex04.shared.gatekeeper --cov-report=term-missing
# Tests with mocked provider — no real API calls
```

---

### Graph Service (T4.01–T4.03)

#### T4.01 — Graph Service: Runner

| Attribute | Value |
|---|---|
| **Status** | Done |
| **Priority** | P0 |
| **PLAN Reference** | [PLAN §3.3 Graph Service — runner.py] |
| **PRD Reference** | [PRD FR-1.1] |
| **Estimate** | 60 min |

**Definition of Done**:

- [ ] `GraphRunner.execute(target_path)` invokes Grphify CLI via subprocess
- [ ] Returns path to generated `graph.json`
- [ ] Handles subprocess failures, missing Grphify, invalid target
- [ ] Logs execution output for debugging
- [ ] File ≤ 150 lines

**Independent Verification**:

```bash
uv run pytest tests/unit/services/graph/test_runner.py -v --cov=ex04.services.graph.runner --cov-report=term-missing
# Tests with mocked subprocess — no real Grphify invocation
```

---

#### T4.02 — Graph Service: Parser

| Attribute | Value |
|---|---|
| **Status** | Done |
| **Priority** | P0 |
| **PLAN Reference** | [PLAN §3.3 Graph Service — parser.py] |
| **PRD Reference** | [PRD FR-1.1] graph.json parsing |
| **Estimate** | 60 min |

**Definition of Done**:

- [x] `GraphParser.parse(graph_path)` reads `graph.json` and returns `GraphData`
- [x] Extracts entities, relationships, communities from Grphify output
- [x] Handles missing fields, malformed JSON, empty graph
- [x] File ≤ 150 lines

**Independent Verification**:

```bash
uv run pytest tests/unit/services/graph/test_parser.py -v --cov=ex04.services.graph.parser --cov-report=term-missing
# Tests with sample graph.json fixtures
```

---

#### T4.03 — Graph Service: Analyzer

| Attribute | Value |
|---|---|
| **Status** | Done |
| **Priority** | P0 |
| **PLAN Reference** | [PLAN §3.3 Graph Service — analyzer.py] |
| **PRD Reference** | [PRD FR-1.4-1.5], [PRD FR-7.2] centrality ranking |
| **Estimate** | 90 min |

**Definition of Done**:

- [x] `GraphAnalyzer.find_god_nodes(graph)` identifies high-degree nodes
- [x] `GraphAnalyzer.rank_by_centrality(graph, ref_node)` ranks by proximity
- [x] `GraphAnalyzer.detect_communities(graph)` extracts community clusters
- [x] All methods have docstrings with I/O contract
- [x] File ≤ 150 lines — split centrality calculation if needed

**Independent Verification**:

```bash
uv run pytest tests/unit/services/graph/test_analyzer.py -v --cov=ex04.services.graph.analyzer --cov-report=term-missing
# Tests with synthetic graph fixtures
```

---

### Vault Service (T4.04–T4.06)

#### T4.04 — Vault Service: Builder

| Attribute | Value |
|---|---|
| **Status** | Done |
| **Priority** | P0 |
| **PLAN Reference** | [PLAN §3.4 Vault Service — builder.py] |
| **PRD Reference** | [PRD FR-2.2-2.3] |
| **Estimate** | 60 min |

**Definition of Done**:

- [x] `VaultBuilder.build(graph)` creates complete vault from graph data
- [x] `VaultBuilder.create_index(graph)` generates `index.md` with navigation structure
- [x] `VaultBuilder.create_hot(focus_area)` generates `hot.md` for bug area
- [x] Uses `[[wikilinks]]` syntax for Obsidian compatibility
- [x] Creates vault directory structure
- [x] File ≤ 150 lines

**Independent Verification**:

```bash
uv run pytest tests/unit/services/vault/test_builder.py -v --cov=ex04.services.vault.builder --cov-report=term-missing
# Verifies generated .md files have correct structure
```

---

#### T4.05 — Vault Service: Navigator

| Attribute | Value |
|---|---|
| **Status** | Done |
| **Priority** | P0 |
| **PLAN Reference** | [PLAN §3.4 Vault Service — navigator.py] |
| **PRD Reference** | [PRD FR-2.5] |
| **Estimate** | 45 min |

**Definition of Done**:

- [x] `VaultNavigator.find_relevant_notes(query)` searches vault by keyword matching
- [x] `VaultNavigator.navigate_from_index(target)` follows wikilinks from index
- [x] Parses `[[wikilinks]]` from Markdown
- [x] Handles missing notes, broken links

**Independent Verification**:

```bash
uv run pytest tests/unit/services/vault/test_navigator.py -v --cov=ex04.services.vault.navigator --cov-report=term-missing
# Tests against test vault fixtures
```

---

#### T4.06 — Vault Service: Note Manager

| Attribute | Value |
|---|---|
| **Status** | Done |
| **Priority** | P0 |
| **PLAN Reference** | [PLAN §3.4 Vault Service — note_manager.py] |
| **PRD Reference** | [PRD FR-2.4] |
| **Estimate** | 45 min |

**Definition of Done**:

- [x] `NoteManager.create_note(title, content, links)` creates linked Markdown note
- [x] `NoteManager.update_note(path, content)` appends to existing note
- [x] Generates proper frontmatter with title, tags, date
- [x] File ≤ 150 lines

**Independent Verification**:

```bash
uv run pytest tests/unit/services/vault/test_note_manager.py -v --cov=ex04.services.vault.note_manager --cov-report=term-missing
```

---

### Agent Service (T4.07–T4.15)

#### T4.07 — Agent Service: State Definition

| Attribute | Value |
|---|---|
| **Status** | Done |
| **Priority** | P0 |
| **PLAN Reference** | [PLAN §3.5 Agent Service — state.py] |
| **PRD Reference** | [PRD FR-4.3] |
| **Estimate** | 20 min |

**Definition of Done**:

- [x] `AgentState` TypedDict defined with all fields from [PLAN §3.5]
- [x] `Suspect` dataclass defined
- [x] Full docstrings

**Independent Verification**:

```bash
uv run python -c "from ex04.services.agent.state import AgentState, Suspect; print('OK')"
```

---

#### T4.08 — Agent Service: Workflow Builder

| Attribute | Value |
|---|---|
| **Status** | Done |
| **Priority** | P0 |
| **PLAN Reference** | [PLAN §3.5 Agent Service — workflow.py] |
| **PRD Reference** | [PRD FR-4.1] |
| **Estimate** | 90 min |

**Definition of Done**:

- [x] `WorkflowBuilder.build()` assembles LangGraph `StateGraph` with all 7 nodes
- [x] `add_nodes()` registers each node function
- [x] `add_edges()` defines control flow: knowledge → analysis → suspect → inspect → rootcause → fix → verify
- [x] Retry loop: verify → suspect (if tests fail)
- [x] Compiled graph is executable
- [x] File ≤ 150 lines

**Independent Verification**:

```bash
uv run pytest tests/unit/services/agent/test_workflow.py -v --cov=ex04.services.agent.workflow --cov-report=term-missing
# Tests graph structure without executing real LLM calls
```

---

#### T4.09 — Agent Service: Knowledge Load Node

| Attribute | Value |
|---|---|
| **Status** | Done |
| **Priority** | P0 |
| **PLAN Reference** | [PLAN §3.5 Agent Service — nodes/knowledge.py] |
| **PRD Reference** | [PRD FR-4.2] |
| **Estimate** | 45 min |

**Definition of Done**:

- [x] Loads graph summary and vault context into `AgentState`
- [x] Limits context to configured token budget
- [x] Callable as LangGraph node: `(state) -> state`

**Independent Verification**:

```bash
uv run pytest tests/unit/services/agent/nodes/test_knowledge.py -v
```

---

#### T4.10 — Agent Service: Bug Analysis Node

| Attribute | Value |
|---|---|
| **Status** | Done |
| **Priority** | P0 |
| **PLAN Reference** | [PLAN §3.5 Agent Service — nodes/analysis.py] |
| **PRD Reference** | [PRD FR-4.4] |
| **Estimate** | 45 min |

**Definition of Done**:

- [x] Analyzes bug report against graph context
- [x] Uses Gatekeeper for LLM call
- [x] Populates initial suspects list
- [x] Callable as LangGraph node

**Independent Verification**:

```bash
uv run pytest tests/unit/services/agent/nodes/test_analysis.py -v
# Uses mock provider via gatekeeper
```

---

#### T4.11 — Agent Service: Suspect Ranking Node

| Attribute | Value |
|---|---|
| **Status** | Done |
| **Priority** | P0 |
| **PLAN Reference** | [PLAN §3.5 Agent Service — nodes/suspect.py] |
| **PRD Reference** | [PRD FR-4.4], [PRD FR-7.2] original extension: centrality ranking |
| **Estimate** | 45 min |

**Definition of Done**:

- [x] Ranks suspects by graph centrality and proximity to failure indicators
- [x] Limits to `max_suspects` from config
- [x] Callable as LangGraph node

**Independent Verification**:

```bash
uv run pytest tests/unit/services/agent/nodes/test_suspect.py -v
```

---

#### T4.12 — Agent Service: Code Inspection Node

| Attribute | Value |
|---|---|
| **Status** | Done |
| **Priority** | P0 |
| **PLAN Reference** | [PLAN §3.5 Agent Service — nodes/inspect.py] |
| **PRD Reference** | [PRD FR-4.2] |
| **Estimate** | 45 min |

**Definition of Done**:

- [x] Fetches code snippets only for ranked suspects (not entire codebase)
- [x] Records files read for comparison metrics
- [x] Uses Gatekeeper for LLM analysis
- [x] Callable as LangGraph node

**Independent Verification**:

```bash
uv run pytest tests/unit/services/agent/nodes/test_inspect.py -v
```

---

#### T4.13 — Agent Service: Root Cause Node

| Attribute | Value |
|---|---|
| **Status** | Done |
| **Priority** | P0 |
| **PLAN Reference** | [PLAN §3.5 Agent Service — nodes/rootcause.py] |
| **PRD Reference** | [PRD FR-4.4] |
| **Estimate** | 45 min |

**Definition of Done**:

- [x] Analyzes inspected code to determine root cause
- [x] Produces structured root cause description
- [x] Uses Gatekeeper for LLM call
- [x] Callable as LangGraph node

**Independent Verification**:

```bash
uv run pytest tests/unit/services/agent/nodes/test_rootcause.py -v
```

---

#### T4.14 — Agent Service: Fix Generation Node

| Attribute | Value |
|---|---|
| **Status** | Done |
| **Priority** | P0 |
| **PLAN Reference** | [PLAN §3.5 Agent Service — nodes/fix.py] |
| **PRD Reference** | [PRD FR-4.5], [PRD FR-5.1] |
| **Estimate** | 45 min |

**Definition of Done**:

- [x] Generates fix based on root cause analysis
- [x] Applies fix to target file
- [x] Records before/after diff
- [x] Uses Gatekeeper for LLM call
- [x] Callable as LangGraph node

**Independent Verification**:

```bash
uv run pytest tests/unit/services/agent/nodes/test_fix.py -v
# Tests on temporary files
```

---

#### T4.15 — Agent Service: Verification Node

| Attribute | Value |
|---|---|
| **Status** | Done |
| **Priority** | P0 |
| **PLAN Reference** | [PLAN §3.5 Agent Service — nodes/verify.py] |
| **PRD Reference** | [PRD FR-4.6] |
| **Estimate** | 45 min |

**Definition of Done**:

- [x] Runs tests on fixed code
- [x] Records test results in state
- [x] Determines whether to iterate or succeed
- [x] Callable as LangGraph node

**Independent Verification**:

```bash
uv run pytest tests/unit/services/agent/nodes/test_verify.py -v
```

---

### Analysis Service (T4.16–T4.18)

#### T4.16 — Analysis Service: Reverse Engineer

| Attribute | Value |
|---|---|
| **Status** | Done |
| **Priority** | P0 |
| **PLAN Reference** | [PLAN §3.6 Analysis Service — reverse_engineer.py] |
| **PRD Reference** | [PRD FR-3.1-3.2] |
| **Estimate** | 60 min |

**Definition of Done**:

- [x] `extract_block_schema(graph)` produces Mermaid block diagram
- [x] `extract_oop_schema(graph)` produces Mermaid class diagram
- [x] `identify_patterns(graph)` detects design patterns
- [x] Uses Gatekeeper for LLM-assisted analysis

**Independent Verification**:

```bash
uv run pytest tests/unit/services/analysis/test_reverse_engineer.py -v --cov=ex04.services.analysis.reverse_engineer --cov-report=term-missing
```

---

#### T4.17 — Analysis Service: Diagram Generator

| Attribute | Value |
|---|---|
| **Status** | Done |
| **Priority** | P1 |
| **PLAN Reference** | [PLAN §3.6 Analysis Service — diagram_gen.py] |
| **PRD Reference** | [PRD FR-3.3] |
| **Estimate** | 30 min |

**Definition of Done**:

- [x] `save_diagram(content, name, path)` writes Mermaid to `.md` file
- [x] `validate_mermaid(content)` checks basic Mermaid syntax
- [x] File ≤ 150 lines

**Independent Verification**:

```bash
uv run pytest tests/unit/services/analysis/test_diagram_gen.py -v
```

---

#### T4.18 — Analysis Service: Bug Reporter

| Attribute | Value |
|---|---|
| **Status** | Done |
| **Priority** | P1 |
| **PLAN Reference** | [PLAN §3.6 Analysis Service — bug_report.py] |
| **PRD Reference** | [PRD FR-5.2] |
| **Estimate** | 30 min |

**Definition of Done**:

- [x] `generate(investigation)` produces structured Markdown report
- [x] Includes: problem, root cause, investigation steps, fix, before/after
- [x] File ≤ 150 lines

**Independent Verification**:

```bash
uv run pytest tests/unit/services/analysis/test_bug_report.py -v
```

---

**Source**: Extracted from [`docs/TODO.md`](../TODO.md) §5.
