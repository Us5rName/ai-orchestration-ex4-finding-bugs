"""Data types for PatchImpactAnalyzer.

Extracted to keep patch_impact.py within the 150-line limit.
"""

from __future__ import annotations

from dataclasses import dataclass, field


@dataclass
class ImpactedNode:
    """A node reachable from a changed symbol within max_depth BFS steps."""

    name: str
    kind: str
    file_path: str
    depth: int
    path_from_changed: list[str] = field(default_factory=list)
    source_anchor: str = ""


@dataclass
class ImpactReport:
    """Report of entities potentially affected by a change.

    Limitations field always notes that graph reachability does not
    prove runtime impact.
    """

    changed_symbols: list[str] = field(default_factory=list)
    direct_dependents: list[ImpactedNode] = field(default_factory=list)
    transitive_dependents: list[ImpactedNode] = field(default_factory=list)
    affected_test_files: list[str] = field(default_factory=list)
    max_depth_used: int = 0
    impact_paths: list[list[str]] = field(default_factory=list)
    limitations: list[str] = field(default_factory=list)
    evidence_class: str = "deterministic_keyless_evidence"
