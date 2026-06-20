# 8. API Contract

[← Back to Home](./Home.md) | [Prev: UML Activity Diagram](./07-UML-Activity-Diagram.md) | [Next: Configuration Schema →](./09-Configuration-Schema.md)

---

## 8.1 SDK Public API

All external consumers interact exclusively through `Ex04SDK`:

```python
# src/ex04/sdk/sdk.py

class Ex04SDK:
    """Single entry point for all EX04 operations."""

    @classmethod
    def from_config(cls, config_path: str) -> "Ex04SDK": ...
    # Reads config/setup.json; concrete wiring in sdk/_wiring.py.

    def run_graphify(self, target_path: str) -> GraphData: ...
    # Extract + parse graph. [PRD FR-1.1]

    def build_vault(self, graph_data: GraphData) -> dict[str, Path]: ...
    # Build Obsidian vault notes. [PRD FR-2.1-2.4]

    def investigate_bug(
        self,
        bug_report: str,
        graph_path: Path | None = None,
        vault_path: Path | None = None,
    ) -> InvestigationResult: ...
    # LangGraph debugging workflow. [PRD FR-4.1-4.6]

    def run_comparison(
        self,
        bug_report: str,
        source_files: list[Path],    # caller-supplied; must be nonempty for meaningful results
        graph_data: GraphData | None = None,
        vault_path: Path | None = None,
    ) -> ComparisonReport: ...
    # Low-level: compare naive vs. graph-guided. [PRD FR-6.1-6.3]

    def compare_target(
        self,
        target_path: str | Path,    # root of the target codebase
        bug_report: str,
    ) -> ComparisonReport: ...
    # High-level: extracts graph, builds vault, discovers sources, runs comparison.
    # Validates target_path exists and is a directory. Used by CLI 'compare'.

    def reverse_engineer(self, target_path: str) -> str: ...
    # Architectural docs from graph. [PRD FR-3.1-3.3]

    def generate_report(self, investigation: InvestigationResult) -> str: ...
    # Structured Markdown bug report.

    def identify_patterns(self, target_path: str) -> list[str]: ...
    # Design pattern identification from graph.

    def detect_orphans(self, graph_data: GraphData, output_dir: Path) -> OrphanReport: ...
    """Find graph entities with no incoming edges and generate doc stubs. [PRD FR-7.5]"""

    def full_pipeline(self, target_path: str, bug_report: str) -> PipelineResult: ...
    # Complete pipeline: graphify → vault → investigate → compare (real sources) → report.
    # Discovers real Python source files deterministically; passes vault dir to comparison.
```

## 8.2 CLI Command Syntax

```bash
python -m ex04 [--config CONFIG] <command> [args]

# Extract code graph
python -m ex04 graphify <target_path>

# Investigate a bug
python -m ex04 investigate "<bug_report>"
python -m ex04 investigate @path/to/bug_report.txt

# Compare naive vs. graph-guided (requires target_path)
python -m ex04 compare <target_path> "<bug_report>"
python -m ex04 compare <target_path> @path/to/bug_report.txt

# Full end-to-end pipeline
python -m ex04 pipeline <target_path> "<bug_report>"
```

Exit codes: 0 = success, 1 = unexpected error, 2 = file not found, 3 = not implemented.

## 8.3 Provider Interface Contract

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
