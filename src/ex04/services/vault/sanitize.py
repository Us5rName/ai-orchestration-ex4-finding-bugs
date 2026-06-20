"""Vault sanitization helpers — safe filenames and YAML frontmatter.

Entity names come from external Grphify output and are used as note
filenames and wikilink targets; they must be neutralized before touching
the filesystem or YAML frontmatter.

Implementation: **Phase 4** (T4.04, hardening)
"""

from __future__ import annotations

import re

# Path separators and characters reserved on common filesystems.
_UNSAFE_CHARS = re.compile(r'[\\/:*?"<>|\x00-\x1f]')
_FALLBACK = "unnamed"


def safe_name(value: str) -> str:
    """Return a filesystem-safe note name derived from ``value``.

    Replaces path separators and reserved characters with ``_`` and strips
    leading/trailing dots and whitespace — preventing ``.``, ``..`` (path
    traversal) and accidental hidden files. Case and the inner characters
    letters, digits, ``.``, ``_`` and ``-`` are preserved so names stay
    readable. Falls back to a placeholder when nothing usable remains.

    Args:
        value: Raw entity name (e.g. a Grphify node id or label).

    Returns:
        A safe filename stem (without extension).
    """
    cleaned = _UNSAFE_CHARS.sub("_", value).strip().strip(".").strip()
    return cleaned or _FALLBACK


def yaml_double_quote(value: str) -> str:
    """Return ``value`` as a YAML-safe double-quoted scalar.

    Escapes backslashes and double quotes so a name containing ``"`` cannot
    break the surrounding frontmatter (e.g. ``title: "..."``).

    Args:
        value: Raw string to embed in double quotes.

    Returns:
        The value wrapped in double quotes with internal quotes escaped.
    """
    escaped = value.replace("\\", "\\\\").replace('"', '\\"')
    return f'"{escaped}"'
