"""Strict structured-output parser shared by comparison runners."""

from __future__ import annotations

import json
import re
from typing import Any

_REQUIRED_KEYS = (
    "root_cause",
    "suspected_files",
    "suspected_symbols",
    "confidence",
    "evidence",
)
_CONFIDENCE = frozenset({"low", "medium", "high"})
_FENCE_RE = re.compile(r"^```(?:json)?\s*|\s*```$", re.DOTALL | re.MULTILINE)

JSON_SCHEMA = (
    "Respond with JSON only: {"
    '"root_cause":"string",'
    '"suspected_files":["path"],'
    '"suspected_symbols":["symbol"],'
    '"confidence":"low|medium|high",'
    '"evidence":[{"file":"path","line_start":1,"line_end":5,'
    '"symbol":"name","reason":"why"}],'
    '"patch":"optional unified diff"}'
)


def parse_json_response(text: str) -> tuple[str, dict[str, object] | None]:
    """Parse and validate the structured investigation response."""
    stripped = text.strip()
    if not stripped:
        return "empty", None
    for candidate in (stripped, _FENCE_RE.sub("", stripped).strip()):
        try:
            data = json.loads(candidate)
        except json.JSONDecodeError:
            continue
        return ("parsed_ok", data) if _valid_payload(data) else ("parse_failed", None)
    return "parse_failed", None


def _valid_payload(data: Any) -> bool:
    """Validate top-level schema and value types."""
    if not isinstance(data, dict) or any(k not in data for k in _REQUIRED_KEYS):
        return False
    if not isinstance(data["root_cause"], str) or not data["root_cause"].strip():
        return False
    if not _string_list(data["suspected_files"]) or not _string_list(
        data["suspected_symbols"]
    ):
        return False
    if data["confidence"] not in _CONFIDENCE:
        return False
    if "patch" in data and not isinstance(data["patch"], str):
        return False
    evidence = data["evidence"]
    return isinstance(evidence, list) and all(_valid_evidence(item) for item in evidence)


def _string_list(value: object) -> bool:
    return isinstance(value, list) and all(isinstance(item, str) for item in value)


def _valid_evidence(item: object) -> bool:
    """Validate one source evidence anchor shape."""
    if not isinstance(item, dict):
        return False
    required = ("file", "line_start", "line_end", "symbol", "reason")
    if any(key not in item for key in required):
        return False
    if not all(isinstance(item[key], str) for key in ("file", "symbol", "reason")):
        return False
    start, end = item["line_start"], item["line_end"]
    return isinstance(start, int) and isinstance(end, int) and 1 <= start <= end
