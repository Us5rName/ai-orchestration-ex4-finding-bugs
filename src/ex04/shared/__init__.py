"""Shared package — contracts and types for cross-cutting infrastructure.

This package defines the **contract layer** for shared infrastructure:
- **Version**: Single source of truth for project version (T2.01)
- **Types**: Pure data classes for graph, metrics, and results (T2.02)
- **ConfigManagerInterface**: Contract for config loading (T2.03, impl in P4)
- **GatekeeperInterface**: Contract for API call routing (T2.04, impl in P4)
- **TokenTrackerInterface**: Contract for token tracking (T2.05, impl in P6)

All interfaces are abstract base classes (ABCs). Concrete implementations
will be provided in later phases where the contracts are consumed.

## Import Guide

```python
# Types (already implemented)
from ex04.shared import GraphData, TokenMetrics, RunMetrics, ...

# Interfaces (contracts only)
from ex04.shared import ConfigManagerInterface, GatekeeperInterface, TokenTrackerInterface

# Version
from ex04.shared import __version__
```
"""

from ex04.shared.config import ConfigManagerInterface
from ex04.shared.gatekeeper import GatekeeperInterface
from ex04.shared.token_tracker import TokenTrackerInterface
from ex04.shared.types import Community, Entity, GraphData, Relationship
from ex04.shared.types_metrics import (
    ComparisonMetrics,
    ComparisonReport,
    RunMetrics,
    TokenMetrics,
)
from ex04.shared.types_results import (
    InvestigationResult,
    PipelineResult,
    ProviderResponse,
    Suspect,
)
from ex04.shared.version import __version__

__all__ = [
    # Version
    "__version__",
    # Config contract — actual impl in Phase 4
    "ConfigManagerInterface",
    # Gatekeeper contract — actual impl in Phase 4
    "GatekeeperInterface",
    # Token tracker contract — actual impl in Phase 6
    "TokenTrackerInterface",
    # Graph types (T2.02)
    "Community",
    "Entity",
    "GraphData",
    "Relationship",
    # Metrics types (T2.02)
    "TokenMetrics",
    "RunMetrics",
    "ComparisonMetrics",
    "ComparisonReport",
    # Result types (T2.02)
    "ProviderResponse",
    "Suspect",
    "InvestigationResult",
    "PipelineResult",
]
