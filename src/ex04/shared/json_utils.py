"""JSON utilities — shared JSON loading with consistent error handling.

Centralises the try/except pattern for reading JSON files so call sites
only handle FileNotFoundError for missing files and ValueError for malformed
content, with a uniform error message format.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any


def load_json(path: Path) -> Any:
    """Load and parse a JSON file.

    Args:
        path: Path to the JSON file.

    Returns:
        Parsed Python object.

    Raises:
        FileNotFoundError: If the file does not exist (propagated from read_text).
        ValueError: If the file content is not valid JSON.
    """
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        raise ValueError(f"Malformed JSON in {path}: {exc}") from exc
