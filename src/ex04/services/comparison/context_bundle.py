"""Typed immutable context bundle for comparison experiments.

The ContextBundle represents the output of a context-acquisition strategy.
It is the experimental treatment variable — the only thing that intentionally
differs between the naive and graph-guided comparison modes.
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum


class ContextStrategy(Enum):
    """Context acquisition strategy — the experimental treatment variable."""

    NAIVE = "naive"
    GRAPH_GUIDED = "graph_guided"


@dataclass(frozen=True, slots=True)
class SourceRef:
    """Reference to one source artifact included in context.

    Attributes:
        path: Filesystem or logical path to the artifact.
        kind: Artifact kind: "file", "node", "edge", "vault_note", etc.
        label: Optional human-readable label.
    """

    path: str
    kind: str
    label: str | None = None


@dataclass(frozen=True, slots=True)
class ContextProvenance:
    """Provenance metadata for a ContextBundle.

    Attributes:
        strategy: The acquisition strategy that produced this bundle.
        token_count: Estimated token count of the context content.
        source_count: Number of source artifacts included.
        extra: Additional key-value provenance pairs (immutable).
    """

    strategy: ContextStrategy
    token_count: int
    source_count: int
    extra: tuple[tuple[str, str], ...] = ()


@dataclass(frozen=True, slots=True)
class ContextBundle:
    """Immutable context bundle produced by a context-acquisition strategy.

    Both comparison modes produce a ContextBundle from their acquisition
    logic. The PromptBuilder consumes it to produce a canonical prompt
    where only the context section differs between modes.

    Attributes:
        content: Raw text context to embed in the prompt.
        strategy: The strategy that produced this bundle.
        source_refs: Ordered, immutable references to included sources.
        provenance: Structured provenance metadata.
    """

    content: str
    strategy: ContextStrategy
    source_refs: tuple[SourceRef, ...]
    provenance: ContextProvenance
