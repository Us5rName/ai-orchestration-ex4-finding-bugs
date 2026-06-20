# 3. Module Design

[← Back to Home](./Home.md) | [Prev: C4 Model](./02-C4-Model.md) | [Next: Data Flow →](./04-Data-Flow.md)

---

Each module is an **independent building block** with a well-defined interface. **No module imports another module's concrete implementation** — all inter-module dependencies flow through `*Interface` abstract classes. This enables **fully parallel development**: every team member works against a stable contract while the actual implementation is built in parallel.

**Contract-First Rule**: For every service `XService`, an `XServiceInterface` ABC is defined **before** implementation begins. Other modules depend only on the interface. At runtime, the SDK injects the concrete implementation.

## 3.1 Module Dependency Graph (Runtime)

Solid arrows = **runtime** dependencies (after SDK wiring). Dashed arrows = **compile-time** interface imports only (no blocking).

```mermaid
graph TD
    SDK["SDK"]

    GI["GraphServiceInterface"]
    G["GraphService"]

    VI["VaultServiceInterface"]
    V["VaultService"]

    PI["ProviderInterface"]
    P["OpenAI/Anthropic Provider"]

    A["Agent Service"]
    AN["Analysis Service"]
    C["Comparison Service"]
    SH["Shared Layer"]

    SDK --> GI
    SDK --> VI
    SDK --> PI
    SDK --> G
    SDK --> V
    SDK --> A
    SDK --> AN
    SDK --> C

    G -.implements.-> GI
    V -.implements.-> VI
    P -.implements.-> PI

    A --> GI
    A --> VI
    A --> PI
    A --> SH

    AN --> GI
    AN --> SH

    C --> GI
    C --> VI
    C --> PI
    C --> SH

    G --> SH
    V --> SH
    P --> SH
```

**Key for parallel development**: `Agent Service`, `Analysis Service`, and `Comparison Service` import only `*Interface` ABCs (zero-cost, no blocking). They never import `GraphService`, `VaultService`, or provider implementations directly.

### 3.1.1 Service Interfaces (Contract Layer)

All interfaces are implemented as ABCs in their respective `interface.py` files. Signatures below match the actual code.

**GraphServiceInterface** (`services/graph/interface.py`, Phase 4 T4.01–T4.03):
```python
@abstractmethod
def extract(self, target_path: str) -> Path: ...
@abstractmethod
def parse(self, graph_path: Path) -> GraphData: ...
@abstractmethod
def analyze(self, graph_data: GraphData) -> dict[str, list]: ...
```

**VaultServiceInterface** (`services/vault/interface.py`, Phase 4 T4.04–T4.06):
```python
@abstractmethod
def build(self, graph_data: GraphData) -> dict[str, Path]: ...
@abstractmethod
def navigate(self, query: str) -> list[dict[str, str]]: ...
@abstractmethod
def update(self, note_type: str, content: str) -> Path: ...
```

**ProviderInterface** (`providers/interface.py`, Phase 3):
```python
@abstractmethod
def chat(
    self,
    messages: list[Message],
    model: str,
    base_url: str | None = None,
) -> ProviderResponse: ...
@abstractmethod
def count_tokens(self, text: str) -> int: ...
```

**AnalysisServiceInterface** (`services/analysis/interface.py`, Phase 4 T4.16–T4.18):
```python
@abstractmethod
def reverse_engineer(self, graph_data: GraphData) -> str: ...
@abstractmethod
def report(self, investigation: InvestigationResult) -> str: ...
```

**AgentServiceInterface** (`services/agent/interface.py`, Phase 4 T4.07–T4.15):
```python
@abstractmethod
def investigate(
    self,
    bug_report: str,
    graph_path: Path | None = None,
    vault_path: Path | None = None,
) -> InvestigationResult: ...
@abstractmethod
def get_state(self) -> dict: ...
```

**ComparisonServiceInterface** (`services/comparison/interface.py`, Phase 6 T6.01–T6.04):
```python
@abstractmethod
def run_comparison(
    self,
    bug_report: str,
    source_files: list[Path],
    graph_data: GraphData | None = None,
    vault_path: Path | None = None,
) -> ComparisonReport: ...
```

| Interface | Path | Defines | Enables Parallel Work For |
|---|---|---|---|
| `GraphServiceInterface` | `services/graph/interface.py` | `extract()`, `parse()`, `analyze()` | Agent, Analysis, Comparison |
| `VaultServiceInterface` | `services/vault/interface.py` | `build()`, `navigate()`, `update()` | Agent, Comparison |
| `ProviderInterface` | `providers/interface.py` | `chat()`, `count_tokens()` | Agent, Comparison |
| `AnalysisServiceInterface` | `services/analysis/interface.py` | `reverse_engineer()`, `report()` | SDK |
| `AgentServiceInterface` | `services/agent/interface.py` | `investigate()`, `get_state()` | SDK |
| `ComparisonServiceInterface` | `services/comparison/interface.py` | `run_comparison()` | SDK |

### 3.1.2 Parallel Development Schedule

```mermaid
gantt
    title Parallel Development Timeline
    dateFormat  HH:mm
    axisFormat %H:%M

    section Phase 1-2
    Shared Layer + Interfaces    :p1, 09:00, 2h

    section Phase 3 (Parallel)
    Graph Implementation         :p2a, 11:00, 3h
    Vault Implementation         :p2b, 11:00, 3h
    Provider Implementation      :p2c, 11:00, 2h

    section Phase 4 (Parallel)
    Agent against mocks          :p3a, 14:00, 3h
    Analysis against mocks       :p3b, 14:00, 2h
    Comparison against mocks     :p3c, 14:00, 2h

    section Phase 5
    SDK wires everything         :p4, 17:00, 1h
```

**Point**: After Phase 2 (interfaces are defined), **Phase 3 and 4 run fully in parallel**. No developer waits for another module's implementation.

## 3.2 SDK Module — Single Entry Point

| Attribute | Value |
|---|---|
| **Path** | `src/ex04/sdk/sdk.py` |
| **Responsibility** | Single entry point for all business operations |
| **PRD Mapping** | [PRD §5.4 FR-4] overall orchestration |

**Input**: Operation mode (`graphify`, `investigate`, `compare`, `reverse_engineer`), target codebase path, configuration.

**Output**: Operation results (graph data, investigation findings, comparison report, diagrams).

**Dependencies**: All service modules (delegates only, no direct LLM calls).

```python
class Ex04SDK:
    """
    Single entry point for all EX04 operations.

    All service dependencies are injected through constructor —
    never hard-imported. Enables parallel development via mock injection.

    Input:  graph (GraphServiceInterface), vault (VaultServiceInterface),
            agent (AgentServiceInterface), comparison (ComparisonServiceInterface),
            analysis (AnalysisServiceInterface), config (dict)
    Output: Operation results (GraphData, InvestigationResult, etc.)
    """

    def __init__(
        self,
        graph: GraphServiceInterface,
        vault: VaultServiceInterface,
        agent: AgentServiceInterface,
        comparison: ComparisonServiceInterface,
        analysis: AnalysisServiceInterface,
        config: dict[str, Any] | None = None,
    ):
        ...

    @classmethod
    def from_config(cls, config_path: str) -> Ex04SDK: ...
    def run_graphify(self, target_path: str) -> GraphData: ...
    def build_vault(self, graph_data: GraphData) -> dict[str, Path]: ...
    def investigate_bug(
        self,
        bug_report: str,
        graph_path: Path | None = None,
        vault_path: Path | None = None,
    ) -> InvestigationResult: ...
    def run_comparison(
        self,
        bug_report: str,
        source_files: list[Path],
        graph_data: GraphData | None = None,
        vault_path: Path | None = None,
    ) -> ComparisonReport: ...
    def reverse_engineer(self, target_path: str) -> str: ...
    def detect_orphans(self, graph_data: GraphData, output_dir: Path) -> OrphanReport: ...
    def full_pipeline(self, target_path: str, bug_report: str) -> PipelineResult: ...
```

`from_config()` is the concrete wiring point: it builds the Phase 4 service facades
(`GraphService`, `VaultService`, `AgentService`, `AnalysisService`) and the
Phase 6-deferred `ComparisonService` facade from `config/setup.json`.

## 3.3 Graph Service — Grphify Integration

| Attribute | Value |
|---|---|
| **Path** | `src/ex04/services/graph/` |
| **Responsibility** | Run Grphify, parse graph output, analyze entity relationships |
| **PRD Mapping** | [PRD §5.1 FR-1.1 to FR-1.5] |

**Sub-modules**:

| File | Responsibility |
|---|---|
| `interface.py` | **Contract** — `GraphServiceInterface` ABC (defined FIRST) |
| `runner.py` | Execute Grphify CLI on target codebase |
| `parser.py` | Parse `graph.json` into structured `GraphData` objects |
| `analyzer.py` | Compute centrality, community detection, God Node identification |

**Input**: Target codebase path (`str`), Grphify configuration (`dict`).

**Output**: `GraphData` — structured graph with entities, relationships, communities.

**Dependencies**: Shared layer (config, file I/O). Other modules depend only on `interface.py`.

```python
# runner.py
class GraphRunner:
    """Run Grphify on a target codebase."""
    def execute(self, target_path: str) -> Path: ...  # returns graph.json path

# parser.py
class GraphParser:
    """Parse Grphify output into structured data."""
    def parse(self, graph_path: Path) -> GraphData: ...

# analyzer.py
class GraphAnalyzer:
    """Analyze graph for centrality, communities, God Nodes."""
    def find_god_nodes(self, graph: GraphData, min_degree: int = 2) -> list[str]: ...
    def rank_by_centrality(self, graph: GraphData, ref_node: str) -> list[tuple[str, float]]: ...
    def detect_communities(self, graph: GraphData) -> list[Community]: ...
```

## 3.4 Vault Service — Obsidian Management

| Attribute | Value |
|---|---|
| **Path** | `src/ex04/services/vault/` |
| **Responsibility** | Build, navigate, and update the Obsidian vault |
| **PRD Mapping** | [PRD §5.2 FR-2.1 to FR-2.5] |

**Sub-modules**:

| File | Responsibility |
|---|---|
| `interface.py` | **Contract** — `VaultServiceInterface` ABC (defined FIRST) |
| `builder.py` | Create vault structure with `index.md`, `hot.md`, component notes |
| `navigator.py` | Query vault for relevant context given a bug description |
| `note_manager.py` | Create, update, link individual notes |

**Input**: Graph data, investigation context, bug description.

**Output**: `dict[str, Path]` — mapping note types to file paths.

**Dependencies**: Shared layer (file I/O, config). Other modules depend only on `interface.py`.

```python
# builder.py
class VaultBuilder:
    """Build Obsidian vault from graph data."""
    def __init__(self, vault_path: Path) -> None: ...
    def build(self, graph_data: GraphData) -> dict[str, Path]: ...

# navigator.py
class VaultNavigator:
    """Navigate vault to find relevant context."""
    def __init__(self, vault_path: Path) -> None: ...
    def navigate(self, query: str) -> list[dict[str, str]]: ...

# note_manager.py
class NoteManager:
    """Manage individual vault notes."""
    def __init__(self, vault_path: Path) -> None: ...
    def create_note(self, title: str, content: str, links: list[str]) -> Path: ...
    def update_note(self, path: Path, content: str) -> None: ...
    def update(self, note_type: str, content: str) -> Path: ...
```

## 3.5 Agent Service — LangGraph Workflow

| Attribute | Value |
|---|---|
| **Path** | `src/ex04/services/agent/` |
| **Responsibility** | Build and execute the graph-guided debugging workflow |
| **PRD Mapping** | [PRD §5.4 FR-4.1 to FR-4.6] |

**Sub-modules**:

| File | Responsibility |
|---|---|
| `interface.py` | **Contract** — `AgentServiceInterface` ABC (defined FIRST) |
| `workflow.py` | Assemble the LangGraph state machine with all nodes |
| `nodes/knowledge.py` | Knowledge Load node — load graph + vault into context |
| `nodes/analysis.py` | Bug Analysis node — analyze bug reports against graph |
| `nodes/suspect.py` | Suspect Ranking node — rank candidates by centrality |
| `nodes/inspect.py` | Code Inspection node — fetch relevant code snippets |
| `nodes/rootcause.py` | Root Cause node — determine exact bug origin |
| `nodes/fix.py` | Fix Generation node — propose and apply code fix |
| `nodes/verify.py` | Verification node — run tests to confirm fix |
| `state.py` | Define the LangGraph state schema |

**Input**: Bug report (`str`), graph data (`GraphData`), vault path (`Path`).

**Output**: `InvestigationResult` — root cause, fix applied, test results, token usage.

**Dependencies**: Provider layer (LLM calls), Graph Service (graph data), Vault Service (vault context), Shared (gatekeeper).

```python
# state.py
class AgentState(TypedDict):
    bug_report: str
    graph_context: str
    vault_context: str
    suspects: list[Suspect]
    inspected_code: str
    root_cause: str
    proposed_fix: str
    fix_applied: bool
    test_results: dict
    token_usage: TokenMetrics

# workflow.py
class WorkflowBuilder:
    """Assemble LangGraph debugging workflow with retry loop."""
    def __init__(self, max_iterations: int = 5) -> None: ...
    def build(self) -> CompiledStateGraph: ...
    def _verify_route(self, state: AgentState) -> str: ...

# nodes/knowledge.py
class KnowledgeLoadNode:
    """Load graph + vault context into agent state."""
    def __call__(self, state: AgentState) -> AgentState: ...

# nodes/analysis.py
class BugAnalysisNode:
    """Analyze bug report against graph context, produce initial suspects."""
    def __call__(self, state: AgentState) -> AgentState: ...

# nodes/suspect.py
class SuspectRankingNode:
    """Rank suspects by graph centrality and proximity to failure."""
    def __call__(self, state: AgentState) -> AgentState: ...

# nodes/inspect.py
class CodeInspectionNode:
    """Fetch code snippets for top-ranked suspects."""
    def __init__(self, target_path: Path) -> None: ...
    def __call__(self, state: AgentState) -> AgentState: ...

# nodes/rootcause.py
class RootCauseNode:
    """Determine exact bug origin from inspected code."""
    def __call__(self, state: AgentState) -> AgentState: ...

# nodes/fix.py
class FixGenerationNode:
    """Propose and apply code fix based on root cause."""
    def __call__(self, state: AgentState) -> AgentState: ...

# nodes/verify.py
class VerificationNode:
    """Run tests to confirm fix, increment iteration counter."""
    def __call__(self, state: AgentState) -> AgentState: ...
```

## 3.6 Analysis Service — Reverse Engineering & Bug Reporting

| Attribute | Value |
|---|---|
| **Path** | `src/ex04/services/analysis/` |
| **Responsibility** | Reverse engineer architecture, generate diagrams, produce bug reports |
| **PRD Mapping** | [PRD §5.3 FR-3.1 to FR-3.3], [PRD §5.5 FR-5.1 to FR-5.4] |

**Sub-modules**:

| File | Responsibility |
|---|---|
| `interface.py` | **Contract** — `AnalysisServiceInterface` ABC (defined FIRST) |
| `reverse_engineer.py` | Extract architectural and OOP schemas from code/graph |
| `diagram_gen.py` | Generate Mermaid diagrams (block diagram, OOP schema) |
| `bug_report.py` | Generate structured bug analysis reports |
| `orphan_detector.py` | Find graph entities with no incoming edges; generate doc stubs (FR-7.5) |

**Input**: Graph data, code snippets, investigation results.

**Output**: `str` — Markdown with Mermaid block diagram, OOP schema, and architectural summary.

**Dependencies**: Graph Service (graph data), Shared (file I/O).

```python
class ReverseEngineer:
    """Extract architectural understanding from code/graph."""
    def extract_block_schema(self, graph: GraphData) -> str: ...  # Mermaid
    def extract_oop_schema(self, graph: GraphData) -> str: ...  # Mermaid
    def reverse_engineer(self, graph_data: GraphData) -> str: ...

class DiagramGenerator:
    """Generate and save diagrams."""
    def save_diagram(self, content: str, name: str, path: Path) -> Path: ...

class BugReporter:
    """Generate structured bug analysis reports."""
    def generate(self, investigation: InvestigationResult) -> str: ...

class OrphanDetector:
    """Find graph entities with no incoming edges and generate documentation stubs. [PRD FR-7.5]"""
    def find_orphans(self, graph: GraphData) -> list[Entity]: ...
    def generate_stub(self, entity: Entity) -> str: ...
    def detect_and_report(self, graph: GraphData, output_dir: Path) -> OrphanReport: ...
```

## 3.7 Comparison Service — Token Savings Proof

| Attribute | Value |
|---|---|
| **Path** | `src/ex04/services/comparison/` |
| **Responsibility** | Run naive baseline and graph-guided approaches, compare metrics |
| **PRD Mapping** | [PRD §5.6 FR-6.1 to FR-6.3] |

**Sub-modules**:

| File | Responsibility |
|---|---|
| `interface.py` | **Contract** — `ComparisonServiceInterface` ABC (defined FIRST) |
| `naive_runner.py` | Execute naive approach (read all raw files, no focus) |
| `graph_guided_runner.py` | Execute graph-guided approach (via vault + graph) |
| `metrics.py` | Calculate token savings, file reads, iteration counts |
| `report_gen.py` | Generate comparison report with tables and charts |

**Input**: Bug report, target codebase path, graph data, vault path.

**Output**: `ComparisonReport` — side-by-side metrics, savings percentage, narrative.

**Dependencies**: Provider layer (LLM calls for both approaches), Graph Service (graph for guided mode), Vault Service (vault for guided mode), Shared (gatekeeper, token tracker).

```python
class NaiveRunner:
    """Run naive baseline: dump all code, no graph guidance."""
    def run(self, bug_report: str, source_files: list[Path]) -> RunMetrics: ...

class GraphGuidedRunner:
    """Run graph-guided: navigate via graph + vault first."""
    def run(self, bug_report: str, graph: GraphData, vault: VaultNavigator) -> RunMetrics: ...

class MetricsCalculator:
    """Compare two runs and calculate savings."""
    def compare(self, naive: RunMetrics, guided: RunMetrics) -> ComparisonMetrics: ...

class ReportGenerator:
    """Generate comparison report."""
    def generate(self, metrics: ComparisonMetrics) -> str: ...
```

## 3.8 Provider Layer — Provider-Agnostic LLM Abstraction

| Attribute | Value |
|---|---|
| **Path** | `src/ex04/providers/` |
| **Responsibility** | Abstract LLM provider behind unified interface |
| **PRD Mapping** | Supports [PRD §1.3 Technology Choices] — no vendor lock-in |

**Sub-modules**:

| File | Responsibility |
|---|---|
| `interface.py` | `ProviderInterface` abstract base class |
| `openai_provider.py` | OpenAI implementation |
| `anthropic_provider.py` | Anthropic implementation |
| `factory.py` | Create provider from configuration |

**Input**: Prompt text, system instructions, model name.

**Output**: `ProviderResponse` — generated text, token counts (input/output), model used.

**Dependencies**: Shared layer (config).

```python
# interface.py
class ProviderInterface(ABC):
    """Abstract interface for LLM providers.

    All LLM calls must flow through this interface to ensure
    provider-agnostic design. The Gatekeeper controls rate limits.
    Supports custom base_url for proxy/local endpoints.
    """

    @abstractmethod
    def chat(
        self,
        messages: list[Message],
        model: str,
        base_url: str | None = None,
    ) -> ProviderResponse: ...

    @abstractmethod
    def count_tokens(self, text: str) -> int: ...

# factory.py
class ProviderFactory:
    """Create provider instance from configuration."""
    @staticmethod
    def create(provider_name: str, config: dict) -> ProviderInterface: ...
    # config must include: name, model, api_key_env, base_url (optional)
```

## 3.9 Shared Layer — Infrastructure

| Attribute | Value |
|---|---|
| **Path** | `src/ex04/shared/` |
| **Responsibility** | Cross-cutting concerns: gatekeeper, config, version, tokens |
| **PRD Mapping** | [PRD §6 Non-Functional Requirements NFR-1 to NFR-10] |

**Sub-modules**:

| File | Responsibility |
|---|---|
| `gatekeeper.py` | Rate limiting, FIFO queue, API call monitoring (implements GatekeeperInterface) |
| `config.py` | Load and validate configuration from JSON/env (implements ConfigManagerInterface) |
| `version.py` | Global version tracking (1.00) |
| `token_tracker.py` | Track token consumption across all providers (TokenTrackerInterface, Phase 6) |
| `types.py` | Re-exports all shared types from sub-modules |
| `types_metrics.py` | TokenMetrics, RunMetrics, ComparisonMetrics, ComparisonReport |
| `types_results.py` | ProviderResponse, Suspect, InvestigationResult, PipelineResult |

```python
# gatekeeper.py
class ApiGatekeeper(GatekeeperInterface):
    """Centralized API call manager with rate limiting and FIFO queue."""
    def __init__(
        self,
        rate_limits_path: str = "",
        provider_configs: dict[str, dict[str, Any]] | None = None,
    ) -> None: ...
    def send(self, provider: str, messages: list[dict[str, str]]) -> ProviderResponse: ...
    def get_call_log(self) -> list[dict[str, Any]]: ...
    def get_queue_status(self) -> dict[str, Any]: ...

# config.py
class ConfigManager(ConfigManagerInterface):
    """JSON configuration manager with dot-notation access."""
    def __init__(self) -> None: ...
    def load(self, path: str) -> dict[str, Any]: ...
    def get(self, key_path: str) -> Any: ...
    def validate(self, config: dict[str, Any]) -> bool: ...

# token_tracker.py (Phase 6 — interface only, implementation deferred)
class TokenTrackerInterface(ABC):
    """Abstract token tracker for cross-session token usage tracking."""
    @abstractmethod
    def record(self, metrics: TokenMetrics) -> None: ...
    @abstractmethod
    def total(self, provider: str) -> int: ...
    @abstractmethod
    def by_session(self, session_id: str) -> dict[str, Any]: ...
    @abstractmethod
    def export(self) -> dict[str, Any]: ...

# types.py — re-exports from sub-modules
types_metrics.py:
@dataclass
class TokenMetrics:
    input_tokens: int = 0
    output_tokens: int = 0
    total_tokens: int = 0
    provider: str = ""
    model: str = ""

@dataclass
class RunMetrics:
    tokens_used: int = 0
    files_read: int = 0
    iterations: int = 0
    time_seconds: float = 0.0
    found_root_cause: bool = False

@dataclass
class ComparisonMetrics:
    naive: RunMetrics = field(default_factory=RunMetrics)
    guided: RunMetrics = field(default_factory=RunMetrics)
    token_savings_pct: float = 0.0
    file_read_savings_pct: float = 0.0
    iteration_savings_pct: float = 0.0

@dataclass
class ComparisonReport:
    metrics: ComparisonMetrics = field(default_factory=ComparisonMetrics)
    narrative: str = ""
    token_savings: int = 0

@dataclass
class OrphanReport:
    orphans: list[Entity] = field(default_factory=list)
    stubs: dict[str, str] = field(default_factory=dict)
    report_path: Path | None = None
    total_entities: int = 0
    orphan_count: int = 0

types_results.py:
@dataclass
class ProviderResponse:
    text: str = ""
    input_tokens: int = 0
    output_tokens: int = 0
    model: str = ""
    provider: str = ""
    timestamp: datetime = field(default_factory=datetime.now)

@dataclass
class Suspect:
    file_path: str
    line_start: int
    line_end: int
    score: float = 0.0
    reason: str = ""

@dataclass
class InvestigationResult:
    root_cause: str = ""
    suspects: list[Suspect] = field(default_factory=list)
    proposed_fix: str = ""
    fix_applied: bool = False
    test_results: dict[str, Any] = field(default_factory=dict)
    token_usage: TokenMetrics = field(default_factory=TokenMetrics)

@dataclass
class PipelineResult:
    graph_result: str = ""
    vault_result: str = ""
    investigation: InvestigationResult = field(default_factory=InvestigationResult)
    comparison: ComparisonReport = field(default_factory=ComparisonReport)
    engineering: str = ""

types.py (core graph types):
@dataclass
class Entity:
    name: str
    kind: str
    file_path: str = ""
    line_range: tuple[int, int] = field(default_factory=lambda: (0, 0))

@dataclass
class Relationship:
    source: str
    target: str
    type: str = ""

@dataclass
class Community:
    name: str
    entities: list[str] = field(default_factory=list)
    size: int = 0

@dataclass
class GraphData:
    entities: list[Entity] = field(default_factory=list)
    relationships: list[Relationship] = field(default_factory=list)
    communities: list[Community] = field(default_factory=list)
```

---

**Navigation**: [← Back to Home](./Home.md) | [Prev: C4 Model](./02-C4-Model.md) | [Next: Data Flow →](./04-Data-Flow.md)
