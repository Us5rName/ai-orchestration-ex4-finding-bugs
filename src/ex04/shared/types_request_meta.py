"""Fairness metadata for comparison requests."""

from __future__ import annotations

import re
from dataclasses import field
from typing import Any

CONTROLLED = "controlled"
MODE_SPECIFIC = "mode_specific"
DERIVED = "derived"
INFORMATIONAL = "informational"
FAIRNESS_CLASSES = frozenset({CONTROLLED, MODE_SPECIFIC, DERIVED, INFORMATIONAL})
LIVE_PROVIDERS = frozenset({"openai", "anthropic", "fake"})
EVIDENCE_CLASSES = frozenset({"live", "deterministic", "fixture", "blocked", "not_applicable"})
POLICY_NAMES = frozenset({
    "prohibited_files_clean", "tests_not_deleted", "assertions_not_weakened",
    "generated_paths_clean", "vendor_paths_clean", "diagnosis_consistent",
})
SHA_RE = re.compile(r"^[0-9a-f]{40,64}$")


def request_field(default: Any = "", fairness: str = CONTROLLED) -> Any:
    """Create a dataclass field with fairness metadata."""
    return field(default=default, metadata={"fairness": fairness})


def list_field(fairness: str = CONTROLLED) -> Any:
    """Create a list field with fairness metadata."""
    return field(default_factory=list, metadata={"fairness": fairness})


def dict_field(fairness: str = CONTROLLED) -> Any:
    """Create a dict field with fairness metadata."""
    return field(default_factory=dict, metadata={"fairness": fairness})
