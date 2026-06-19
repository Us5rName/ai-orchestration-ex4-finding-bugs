# 5. Phase 4 — Services

[← Back to Home](./Home.md)

**Goal**: Implement all domain services. Each service imports only `*Interface` contracts — never concrete implementations from other services. Real wiring happens through SDK at runtime ([ADR-006]).

## Task Index

| Task | Service | Link |
|---|---|---|
| T4.01–T4.03 | Graph Service | See below |
| T4.04–T4.06 | Vault Service | See below |
| T4.07–T4.15 | Agent Service | See below |
| T4.16–T4.18 | Analysis Service | See below |

---

### Graph Service (T4.01–T4.03)

#### T4.01 — Graph Service: Runner

| Attribute | Value |
|---|---|
| **Status** | Not Started |
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
| **Status** | Not Started |
| **Priority** | P0 |
| **PLAN Reference** | [PLAN §3.3 Graph Service — parser.py] |
| **PRD Reference** | [PRD FR-1.2] |
| **Estimate** | 60 min |

**Definition of Done**:

- [ ] `GraphParser.parse(graph_path)` reads `graph.json` and returns `GraphData`
- [ ] Extracts entities, relationships, communities from Grphify output
- [ ] Handles missing fields, malformed JSON, empty graph
- [ ] File ≤ 150 lines

**Independent Verification**:

```bash
uv run pytest tests/unit/services/graph/test_parser.py -v --cov=ex04.services.graph.parser --cov-report=term-missing
# Tests with sample graph.json fixtures
```

---

#### T4.03 — Graph Service: Analyzer

| Attribute | Value |
|---|---|
| **Status** | Not Started |
| **Priority** | P0 |
| **PLAN Reference** | [PLAN §3.3 Graph Service — analyzer.py] |
| **PRD Reference** | [PRD FR-1.4-1.5], [PRD FR-7.2] centrality ranking |
| **Estimate** | 90 min |

**Definition of Done**:

- [ ] `GraphAnalyzer.find_god_nodes(graph)` identifies high-degree nodes
- [ ] `GraphAnalyzer.rank_by_centrality(graph, ref_node)` ranks by proximity
- [ ] `GraphAnalyzer.detect_communities(graph)` extracts community clusters
- [ ] All methods have docstrings with I/O contract
- [ ] File ≤ 150 lines — split centrality calculation if needed

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
| **Status** | Not Started |
| **Priority** | P0 |
| **PLAN Reference** | [PLAN §3.4 Vault Service — builder.py] |
| **PRD Reference** | [PRD FR-2.2-2.3] |
| **Estimate** | 60 min |

**Definition of Done**:

- [ ] `VaultBuilder.build(graph)` creates complete vault from graph data
- [ ] `VaultBuilder.create_index(graph)` generates `index.md` with navigation structure
- [ ] `VaultBuilder.create_hot(focus_area)` generates `hot.md` for bug area
- [ ] Uses `[[wikilinks]]` syntax for Obsidian compatibility
- [ ] Creates vault directory structure
- [ ] File ≤ 150 lines

**Independent Verification**:

```bash
uv run pytest tests/unit/services/vault/test_builder.py -v --cov=ex04.services.vault.builder --cov-report=term-missing
# Verifies generated .md files have correct structure
```

---

#### T4.05 — Vault Service: Navigator

| Attribute | Value |
|---|---|
| **Status** | Not Started |
| **Priority** | P0 |
| **PLAN Reference** | [PLAN §3.4 Vault Service — navigator.py] |
| **PRD Reference** | [PRD FR-2.5] |
| **Estimate** | 45 min |

**Definition of Done**:

- [ ] `VaultNavigator.find_relevant_notes(query)` searches vault by keyword matching
- [ ] `VaultNavigator.navigate_from_index(target)` follows wikilinks from index
- [ ] Parses `[[wikilinks]]` from Markdown
- [ ] Handles missing notes, broken links

**Independent Verification**:

```bash
uv run pytest tests/unit/services/vault/test_navigator.py -v --cov=ex04.services.vault.navigator --cov-report=term-missing
# Tests against test vault fixtures
```

---

#### T4.06 — Vault Service: Note Manager

| Attribute | Value |
|---|---|
| **Status** | Not Started |
| **Priority** | P0 |
| **PLAN Reference** | [PLAN §3.4 Vault Service — note_manager.py] |
| **PRD Reference** | [PRD FR-2.4] |
| **Estimate** | 45 min |

**Definition of Done**:

- [ ] `NoteManager.create_note(title, content, links)` creates linked Markdown note
- [ ] `NoteManager.update_note(path, content)` appends to existing note
- [ ] Generates proper frontmatter with title, tags, date
- [ ] File ≤ 150 lines

**Independent Verification**:

```bash
uv run pytest tests/unit/services/vault/test_note_manager.py -v --cov=ex04.services.vault.note_manager --cov-report=term-missing
```

---

### Agent Service (T4.07–T4.15)

#### T4.07 — Agent Service: State Definition

| Attribute | Value |
|---|---|
| **Status** | Not Started |
| **Priority** | P0 |
| **PLAN Reference** | [PLAN §3.5 Agent Service — state.py] |
| **PRD Reference** | [PRD FR-4.3] |
| **Estimate** | 20 min |

**Definition of Done**:

- [ ] `AgentState` TypedDict defined with all fields from [PLAN §3.5]
- [ ] `Suspect` dataclass defined
- [ ] Full docstrings

**Independent Verification**:

```bash
uv run python -c "from ex04.services.agent.state import AgentState, Suspect; print('OK')"
```

---

#### T4.08 — Agent Service: Workflow Builder

| Attribute | Value |
|---|---|
| **Status** | Not Started |
| **Priority** | P0 |
| **PLAN Reference** | [PLAN §3.5 Agent Service — workflow.py] |
| **PRD Reference** | [PRD FR-4.1] |
| **Estimate** | 90 min |

**Definition of Done**:

- [ ] `WorkflowBuilder.build()` assembles LangGraph `StateGraph` with all 7 nodes
- [ ] `add_nodes()` registers each node function
- [ ] `add_edges()` defines control flow: knowledge → analysis → suspect → inspect → rootcause → fix → verify
- [ ] Retry loop: verify → suspect (if tests fail)
- [ ] Compiled graph is executable
- [ ] File ≤ 150 lines

**Independent Verification**:

```bash
uv run pytest tests/unit/services/agent/test_workflow.py -v --cov=ex04.services.agent.workflow --cov-report=term-missing
# Tests graph structure without executing real LLM calls
```

---

#### T4.09 — Agent Service: Knowledge Load Node

| Attribute | Value |
|---|---|
| **Status** | Not Started |
| **Priority** | P0 |
| **PLAN Reference** | [PLAN §3.5 Agent Service — nodes/knowledge.py] |
| **PRD Reference** | [PRD FR-4.2] |
| **Estimate** | 45 min |

**Definition of Done**:

- [ ] Loads graph summary and vault context into `AgentState`
- [ ] Limits context to configured token budget
- [ ] Callable as LangGraph node: `(state) -> state`

**Independent Verification**:

```bash
uv run pytest tests/unit/services/agent/nodes/test_knowledge.py -v
```

---

#### T4.10 — Agent Service: Bug Analysis Node

| Attribute | Value |
|---|---|
| **Status** | Not Started |
| **Priority** | P0 |
| **PLAN Reference** | [PLAN §3.5 Agent Service — nodes/analysis.py] |
| **PRD Reference** | [PRD FR-4.4] |
| **Estimate** | 45 min |

**Definition of Done**:

- [ ] Analyzes bug report against graph context
- [ ] Uses Gatekeeper for LLM call
- [ ] Populates initial suspects list
- [ ] Callable as LangGraph node

**Independent Verification**:

```bash
uv run pytest tests/unit/services/agent/nodes/test_analysis.py -v
# Uses mock provider via gatekeeper
```

---

#### T4.11 — Agent Service: Suspect Ranking Node

| Attribute | Value |
|---|---|
| **Status** | Not Started |
| **Priority** | P0 |
| **PLAN Reference** | [PLAN §3.5 Agent Service — nodes/suspect.py] |
| **PRD Reference** | [PRD FR-4.4], [PRD FR-7.2] original extension: centrality ranking |
| **Estimate** | 45 min |

**Definition of Done**:

- [ ] Ranks suspects by graph centrality and proximity to failure indicators
- [ ] Limits to `max_suspects` from config
- [ ] Callable as LangGraph node

**Independent Verification**:

```bash
uv run pytest tests/unit/services/agent/nodes/test_suspect.py -v
```

---

#### T4.12 — Agent Service: Code Inspection Node

| Attribute | Value |
|---|---|
| **Status** | Not Started |
| **Priority** | P0 |
| **PLAN Reference** | [PLAN §3.5 Agent Service — nodes/inspect.py] |
| **PRD Reference** | [PRD FR-4.2] |
| **Estimate** | 45 min |

**Definition of Done**:

- [ ] Fetches code snippets only for ranked suspects (not entire codebase)
- [ ] Records files read for comparison metrics
- [ ] Uses Gatekeeper for LLM analysis
- [ ] Callable as LangGraph node

**Independent Verification**:

```bash
uv run pytest tests/unit/services/agent/nodes/test_inspect.py -v
```

---

#### T4.13 — Agent Service: Root Cause Node

| Attribute | Value |
|---|---|
| **Status** | Not Started |
| **Priority** | P0 |
| **PLAN Reference** | [PLAN §3.5 Agent Service — nodes/rootcause.py] |
| **PRD Reference** | [PRD FR-4.4] |
| **Estimate** | 45 min |

**Definition of Done**:

- [ ] Analyzes inspected code to determine root cause
- [ ] Produces structured root cause description
- [ ] Uses Gatekeeper for LLM call
- [ ] Callable as LangGraph node

**Independent Verification**:

```bash
uv run pytest tests/unit/services/agent/nodes/test_rootcause.py -v
```

---

#### T4.14 — Agent Service: Fix Generation Node

| Attribute | Value |
|---|---|
| **Status** | Not Started |
| **Priority** | P0 |
| **PLAN Reference** | [PLAN §3.5 Agent Service — nodes/fix.py] |
| **PRD Reference** | [PRD FR-4.5], [PRD FR-5.1] |
| **Estimate** | 45 min |

**Definition of Done**:

- [ ] Generates fix based on root cause analysis
- [ ] Applies fix to target file
- [ ] Records before/after diff
- [ ] Uses Gatekeeper for LLM call
- [ ] Callable as LangGraph node

**Independent Verification**:

```bash
uv run pytest tests/unit/services/agent/nodes/test_fix.py -v
# Tests on temporary files
```

---

#### T4.15 — Agent Service: Verification Node

| Attribute | Value |
|---|---|
| **Status** | Not Started |
| **Priority** | P0 |
| **PLAN Reference** | [PLAN §3.5 Agent Service — nodes/verify.py] |
| **PRD Reference** | [PRD FR-4.6] |
| **Estimate** | 45 min |

**Definition of Done**:

- [ ] Runs tests on fixed code
- [ ] Records test results in state
- [ ] Determines whether to iterate or succeed
- [ ] Callable as LangGraph node

**Independent Verification**:

```bash
uv run pytest tests/unit/services/agent/nodes/test_verify.py -v
```

---

### Analysis Service (T4.16–T4.18)

#### T4.16 — Analysis Service: Reverse Engineer

| Attribute | Value |
|---|---|
| **Status** | Not Started |
| **Priority** | P0 |
| **PLAN Reference** | [PLAN §3.6 Analysis Service — reverse_engineer.py] |
| **PRD Reference** | [PRD FR-3.1-3.2] |
| **Estimate** | 60 min |

**Definition of Done**:

- [ ] `extract_block_schema(graph)` produces Mermaid block diagram
- [ ] `extract_oop_schema(graph)` produces Mermaid class diagram
- [ ] `identify_patterns(graph)` detects design patterns
- [ ] Uses Gatekeeper for LLM-assisted analysis

**Independent Verification**:

```bash
uv run pytest tests/unit/services/analysis/test_reverse_engineer.py -v --cov=ex04.services.analysis.reverse_engineer --cov-report=term-missing
```

---

#### T4.17 — Analysis Service: Diagram Generator

| Attribute | Value |
|---|---|
| **Status** | Not Started |
| **Priority** | P1 |
| **PLAN Reference** | [PLAN §3.6 Analysis Service — diagram_gen.py] |
| **PRD Reference** | [PRD FR-3.3] |
| **Estimate** | 30 min |

**Definition of Done**:

- [ ] `save_diagram(content, name, path)` writes Mermaid to `.md` file
- [ ] `validate_mermaid(content)` checks basic Mermaid syntax
- [ ] File ≤ 150 lines

**Independent Verification**:

```bash
uv run pytest tests/unit/services/analysis/test_diagram_gen.py -v
```

---

#### T4.18 — Analysis Service: Bug Reporter

| Attribute | Value |
|---|---|
| **Status** | Not Started |
| **Priority** | P1 |
| **PLAN Reference** | [PLAN §3.6 Analysis Service — bug_report.py] |
| **PRD Reference** | [PRD FR-5.2] |
| **Estimate** | 30 min |

**Definition of Done**:

- [ ] `generate(investigation)` produces structured Markdown report
- [ ] Includes: problem, root cause, investigation steps, fix, before/after
- [ ] File ≤ 150 lines

**Independent Verification**:

```bash
uv run pytest tests/unit/services/analysis/test_bug_report.py -v
```

---

**Source**: Extracted from [`docs/TODO.md`](../TODO.md) §5.
