<!-- GENERATED FROM CANONICAL DOCUMENTATION - DO NOT EDIT DIRECTLY -->

# 5. Phase 4 — Services

[Back to Home](./Home.md)

**Goal**: Implement all domain services and shared layer contracts deferred from Phase 2. Each service imports only `*Interface` contracts — never concrete implementations from other services. Real wiring happens through SDK at runtime ([ADR-005]).

> **Rationale for T4.00–T4.002**: `ConfigManagerInterface` and `GatekeeperInterface` were defined as contracts in Phase 2 ([PLAN §3.9]) with "impl in P4" comments. All domain services depend on these. Implemented here as prerequisites before any service work.

### T4.00 — Config Manager Implementation

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

### T4.002 — Gatekeeper Implementation

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

### T4.01 — Graph Service: Runner

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

### T4.02 — Graph Service: Parser

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

### T4.03 — Graph Service: Analyzer

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

### T4.19 — Typed Graph Reader Facade

| Attribute | Value |
|---|---|
| **Status** | Done |
| **Priority** | P1 |
| **Execution Order** | 1st of 6 remaining tasks |
| **PLAN Reference** | [PLAN §3.3 Graph Service], [PLAN ADR-007] |
| **PRD Reference** | [PRD-GGI §GraphReader], [PRD §5.7 FR-7.7] |
| **Prerequisite sub-step** | T4.19a — Enrich canonical graph model and parser (Done) |
| **Depends On** | T4.02 GraphParser (Done) |
| **Enables** | T4.20 WeaknessDetector, T6.09 GraphDiff, T6.05 GraphReader integration |
| **Estimate** | 60 min |

**Purpose**: Provide a typed, read-only query facade over parsed `GraphData` so all graph consumers access graph structure through a single canonical boundary rather than rebuilding indexes independently. This is the graph read boundary mandated by [PLAN ADR-007].

**T4.19a — Enrichment Prerequisite (must be completed before implementing GraphReader)**:

The current `Entity` and `Relationship` types in `src/ex04/shared/types.py` do not carry the fields required by several GraphReader, WeaknessDetector, and GraphDiff contracts. T4.19 implementation must first extend these types — or introduce lossless wrappers — so that the single `GraphParser` path preserves all required information.

Required enriched model (planned — not yet implemented):

```python
@dataclass
class Entity:
    id: str                              # stable graph node ID (not display name)
    label: str                           # display name (was: name)
    kind: str
    file_path: str | None = None
    line_range: tuple[int, int] | None = None
    community: int | None = None
    metadata: Mapping[str, object] = field(default_factory=dict)

@dataclass
class Relationship:
    key: str                             # unique edge identity (enables parallel edges)
    source_id: str                       # stable source entity ID
    target_id: str                       # stable target entity ID
    type: str = ""
    confidence: str | None = None        # None = unknown; never upgraded to extracted fact
    confidence_score: float | None = None
    weight: float | None = None
    source_anchor: str | None = None     # "file:start-end" relative path
    metadata: Mapping[str, object] = field(default_factory=dict)
```

**One-parser-path rule**: All enrichment must happen inside the existing `GraphParser`. GraphReader and GraphDiff must not open or re-parse `graph.json` independently.

**Without T4.19a**: T4.20 cannot detect low-confidence relationships; T6.09 cannot classify changed relationships by confidence/weight/anchor; T4.19 cannot distinguish stable ID from display name; parallel edges cannot be preserved.

**Planned file**: `src/ex04/services/graph/reader.py`

**Exact Contract**:

```python
class GraphReader:
    """Canonical typed read-only query facade over GraphData. [ADR-007]

    Accepts existing GraphData or delegates parsing to GraphParser via path constructor.
    Maintains constructor-time indexes for entity lookup, outgoing/incoming/incident
    edges, degree, and community membership. All results are deterministically ordered.
    Never creates a second raw-JSON parsing path.
    """

    def __init__(self, graph_data: GraphData) -> None: ...

    @classmethod
    def from_path(cls, graph_path: Path) -> "GraphReader": ...
    # Delegates to GraphParser — does not create a second raw-JSON parsing path.

    def node(self, node_id: str) -> Entity | None: ...
    # Returns None for unknown node IDs. edges_of() returns empty tuple for unknown nodes.
    # Uses stable entity ID (not display name) as identity.

    def all_nodes(self) -> tuple[Entity, ...]: ...
    # Deterministic ordering by stable entity ID. Immutable result.

    def edges_of(
        self,
        node_id: str,
        *,
        direction: EdgeDirection = EdgeDirection.BOTH,
    ) -> tuple[Relationship, ...]: ...
    # Preserves direction, type, and parallel relationships.
    # Returns empty tuple for unknown node IDs — never raises.

    def top_n_by_degree(self, n: int) -> tuple[tuple[Entity, int], ...]: ...
    # Raises ValueError for n < 0. Deterministic tie-breaking (stable ID sort).

    def communities(self) -> Mapping[str, tuple[Entity, ...]]: ...
    # Key: community name/ID. Entities within each community in stable order.
```

**Semantics to preserve**:
- Stable entity IDs are identity — not display names.
- Relationship direction and type are preserved.
- Parallel relationships (multiple edges between same entities) are preserved.
- Missing confidence is `unknown/unspecified`; never silently upgraded to extracted fact.
- Inexpensive indexes (degree, adjacency) computed eagerly at construction.
- Expensive metrics (exact betweenness centrality) computed lazily and cached.
- Return types are immutable or read-only (no mutation through returned objects).

**Edge cases to handle**:
- Empty graph → valid reader with empty results.
- Isolated nodes → included in `all_nodes()`, degree 0.
- Unknown node ID in `node()` → return `None` (decided: never raise). Unknown node in `edges_of()` → return empty tuple.
- Duplicate display names → resolved by stable entity ID.
- Edge-only malformed graphs → log warning; return best-effort results.
- Invalid graph artifacts → raise `InvalidGraphError` with context.
- `n < 0` in `top_n_by_degree` → raise `ValueError`.

**Implementation subtasks**:
1. Create `src/ex04/services/graph/reader.py` with `GraphReader` class.
2. Add constructor-time index building for outgoing/incoming/incident edges and degree.
3. Implement `from_path()` delegating to existing `GraphParser`.
4. Implement direction-aware `edges_of()`.
5. Implement deterministic `top_n_by_degree()` with tie-breaking.
6. Implement community grouping via `communities()`.
7. Update `graph/__init__.py` to export `GraphReader`.

**Tests required** (`tests/unit/services/graph/test_reader.py`):
- Happy path: node lookup by ID, all_nodes, edges_of (each direction), top_n_by_degree, communities.
- Missing node → None / empty list.
- Isolated node → degree 0, included in all_nodes.
- Empty graph → valid reader.
- Invalid `n` → ValueError.
- Parallel relationships → all preserved.
- Relationship direction accuracy.
- Deterministic ordering verification.

**Non-goals**:
- Do not reimplement graph parsing (delegate to `GraphParser`).
- Do not compute betweenness centrality eagerly.
- Do not add write operations.
- Do not add provider calls or external I/O.

**Definition of Done** (T4.19 is Done only when):
- [ ] `GraphReader` accepts `GraphData` and path-based construction through `GraphParser`.
- [ ] Directed, typed, parallel relationships are preserved.
- [ ] Required indexes and typed operations exist.
- [ ] Ordering and ties are deterministic.
- [ ] Edge cases and invalid input are tested.
- [ ] Relevant consumers reuse it without duplicating graph indexes.
- [ ] SDK-facing behavior remains stable.
- [ ] Documentation and evidence are synchronized.

**Independent Verification**:

```bash
uv run pytest tests/unit/services/graph/test_reader.py -v
```

---

### T4.04 — Vault Service: Builder

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

### T4.05 — Vault Service: Navigator

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

### T4.06 — Vault Service: Note Manager

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

### T4.07 — Agent Service: State Definition

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

### T4.08 — Agent Service: Workflow Builder

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

### T4.09 — Agent Service: Knowledge Load Node

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

### T4.10 — Agent Service: Bug Analysis Node

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

### T4.11 — Agent Service: Suspect Ranking Node

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

### T4.12 — Agent Service: Code Inspection Node

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

### T4.13 — Agent Service: Root Cause Node

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

### T4.14 — Agent Service: Fix Generation Node

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

### T4.15 — Agent Service: Verification Node

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

### T4.16 — Analysis Service: Reverse Engineer

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

### T4.17 — Analysis Service: Diagram Generator

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

### T4.18 — Analysis Service: Bug Reporter

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

### T4.20 — Multi-Signal Weakness Detector

| Attribute | Value |
|---|---|
| **Status** | Not Started |
| **Priority** | P1 |
| **Execution Order** | 3rd of 6 remaining tasks (after T4.19, T5.03) |
| **PLAN Reference** | [PLAN §3.6 Analysis Service] |
| **PRD Reference** | [PRD §5.7 FR-7.7], [PRD-EXT §EXT-3] |
| **Depends On** | T4.19 GraphReader (must exist for detector to consume it) |
| **Estimate** | 90 min |

**Purpose**: Implement a configurable, multi-signal weakness detector over graph and source evidence. Produces typed findings with stable IDs, severity, confidence, evidence anchors, and deterministic ranking. Satisfies FR-7.7.

**Planned package**: `src/ex04/services/analysis/weakness_detector/`

```
__init__.py
models.py        — WeaknessFinding, WeaknessReport, signal/severity/confidence enums
config.py        — load and validate signal configuration
detector.py      — WeaknessDetector orchestration (detect→normalize→deduplicate→rank→render)
ranking.py       — deterministic finding ranking and coalescing
signals_graph.py — high-degree, isolated-component signals (reuse OrphanDetector logic)
signals_paths.py — broken-dependency-path signal
signals_source.py — semantic-duplicate signal (AST-aware Python analysis)
```

**Required Signals**:

| # | Signal | Key Constraint |
|---|---|---|
| 1 | High-degree entity | Not automatically a cross-community bridge; state this explicitly |
| 2 | Isolated / weakly connected component | Not automatically a defect; reuse `OrphanDetector` logic |
| 3 | Ambiguous / unknown / low-confidence relationship | Missing confidence → `unknown`, not extracted fact |
| 4 | Broken dependency path | Missing source anchors are source-validation failures, not broken paths |
| 5 | Semantic duplicate | Python analysis must use AST, not regex over source text |

**Finding Contract**:

```python
@dataclass(frozen=True, slots=True)
class EvidenceAnchor:
    file_path: str
    start_line: int | None
    end_line: int | None
    entity_id: str | None

@dataclass(frozen=True, slots=True)
class RelationshipKey:
    source_id: str
    target_id: str
    relationship_type: str
    parallel_key: str | None

@dataclass(frozen=True, slots=True)
class WeaknessFinding:
    finding_id: str                          # Stable, deterministic ID
    signal_type: SignalType                  # Enum: HIGH_DEGREE, ISOLATED_COMPONENT, etc.
    severity: Severity                       # Enum: HIGH, MEDIUM, LOW, INFO
    confidence: Confidence                   # Enum: HIGH, MEDIUM, LOW, UNKNOWN
    normalized_score: float                  # In [0.0, 1.0]
    entity_ids: tuple[str, ...]              # Stable entity IDs (immutable)
    relationship_keys: tuple[RelationshipKey, ...]  # Typed relationship identities
    evidence: tuple[EvidenceAnchor, ...]     # Typed, typed evidence anchors
    limitations: tuple[str, ...]             # What the finding does NOT prove
    description: str                         # Human-readable; no overclaiming
```

**Constraints**:
- No production hard-coded repository-specific node IDs, file paths, or symbol names.
- Every signal is independently testable and configurable (enable/disable per signal).
- Finding prose must not claim more than the measured evidence supports.
- Isolated-component detection must reuse or adapt `OrphanDetector` — do not reimplement connected-component analysis.
- Detector must consume `GraphReader` rather than rebuilding indexes independently.
- Semantic duplicate analysis must be AST-aware.

**Implementation subtasks**:
1. Create `weakness_detector/models.py` with `WeaknessFinding`, `WeaknessReport`, enums.
2. Create `weakness_detector/config.py` with signal enable/disable and threshold configuration.
3. Create `weakness_detector/signals_graph.py` — high-degree and isolated-component signals; reuse `OrphanDetector`.
4. Create `weakness_detector/signals_paths.py` — broken dependency path signal.
5. Create `weakness_detector/signals_source.py` — AST-aware semantic duplicate signal.
6. Create `weakness_detector/ranking.py` — deterministic score normalization and ranking.
7. Create `weakness_detector/detector.py` — orchestration (detect → normalize → deduplicate → rank).
8. Add `Ex04SDK.detect_weaknesses(graph_data)` (planned method, not yet implemented).

**Tests required** (`tests/unit/services/analysis/test_weakness_detector.py`):
- Each signal independently: expected finding for known-topology graph.
- Empty graph → empty WeaknessReport with no findings.
- Missing source anchors → source-validation failure, not broken dependency path.
- High-degree node → finding does not assert cross-community bridge.
- Isolated component → finding includes limitations statement.
- Semantic duplicate → verified against AST, not text match.
- Combined ranking → deterministic order verified.
- Signal disable → disabled signal produces no findings.

**Non-goals**:
- Do not hard-code any repository-specific node IDs.
- Do not claim runtime impact from graph reachability alone.
- Do not reimplement connected-component analysis (reuse `OrphanDetector`).

**Definition of Done** (T4.20 is Done only when):
- [ ] All five signals implemented generically.
- [ ] Findings are typed, evidence-anchored, deterministic, and deduplicated.
- [ ] No repository-specific production constants exist.
- [ ] Orphan/component behavior reuses existing analysis logic.
- [ ] Python semantic analysis is AST-aware.
- [ ] Individual signal, combined ranking, edge-case, and SDK tests pass.
- [ ] Reports do not overstate evidence.

**Independent Verification**:

```bash
uv run pytest tests/unit/services/analysis/test_weakness_detector.py -v
```

---
