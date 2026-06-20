# 8. API Contract

[← Back to Home](./Home.md) | [Prev: UML Activity Diagram](./07-UML-Activity-Diagram.md) | [Next: Configuration Schema →](./09-Configuration-Schema.md)

---

## 8.1 SDK Public API

All external consumers interact exclusively through `Ex04SDK`:

```python
# src/ex04/sdk/sdk.py

class Ex04SDK:
    """
    Single entry point for all EX04 operations.

    Orchestrates graph extraction, vault building, agent investigation,
    reverse engineering, and token comparison.

    Usage:
        sdk = Ex04SDK.from_config("config/setup.json")
        result = sdk.full_pipeline("graph-home/.graphify/repos/andela/buggy-python")
    """

    @classmethod
    def from_config(cls, config_path: str) -> "Ex04SDK": ...

    def run_graphify(self, target_path: str) -> GraphResult: ...
    """Run Grphify on target codebase. [PRD FR-1.1]"""

    def build_vault(self, graph: GraphData) -> VaultResult: ...
    """Build Obsidian vault from graph data. [PRD FR-2.1-2.4]"""

    def investigate_bug(self, bug_report: str) -> InvestigationResult: ...
    """Run LangGraph debugging workflow. [PRD FR-4.1-4.6]"""

    def run_comparison(self, bug_report: str) -> ComparisonReport: ...
    """Compare naive vs graph-guided token usage. [PRD FR-6.1-6.3]"""

    def reverse_engineer(self, target_path: str) -> EngineeringResult: ...
    """Extract architectural and OOP schemas. [PRD FR-3.1-3.3]"""

    def detect_orphans(self, graph_data: GraphData, output_dir: Path) -> OrphanReport: ...
    """Find graph entities with no incoming edges and generate doc stubs. [PRD FR-7.5]"""

    def full_pipeline(self, target_path: str, bug_report: str) -> PipelineResult: ...
    """Execute complete pipeline: graphify → vault → investigate → compare → report."""
```

## 8.2 Provider Interface Contract

```python
# src/ex04/providers/interface.py

class ProviderInterface(ABC):
    """All LLM providers must implement this interface. [ADR-002]"""

    @abstractmethod
    def chat(
        self,
        messages: list[Message],
        model: str | None = None,
        base_url: str | None = None,
    ) -> ProviderResponse: ...

    @abstractmethod
    def count_tokens(self, text: str) -> int: ...

class ProviderResponse:
    """Standardized response from any LLM provider."""
    text: str
    input_tokens: int
    output_tokens: int
    model: str
    provider: str
    timestamp: datetime
```

---

**Navigation**: [← Back to Home](./Home.md) | [Prev: UML Activity Diagram](./07-UML-Activity-Diagram.md) | [Next: Configuration Schema →](./09-Configuration-Schema.md)
