"""Graph enumeration types for T4.19a enrichment.

ConfidenceState and EdgeDirection used by Entity, Relationship,
and GraphReader. Traceability: [TODO T4.19a], [PLAN ADR-007].
"""

from __future__ import annotations

from enum import StrEnum


class ConfidenceState(StrEnum):
    """Confidence level of a relationship derived from graph analysis.

    UNKNOWN is the default when confidence metadata is absent — never
    silently upgraded to EXTRACTED.
    """

    EXTRACTED = "extracted"
    INFERRED = "inferred"
    UNKNOWN = "unknown"


class EdgeDirection(StrEnum):
    """Direction filter for GraphReader.edges_of()."""

    OUTGOING = "outgoing"
    INCOMING = "incoming"
    BOTH = "both"
