"""Shared JSON output parser for investigation runners.

Both NaiveRunner and GraphGuidedRunner require structured JSON output.
Centralising the parser avoids duplication (DRY).

Traceability: [TODO P6-R03-REV], [Correction #3]
"""

from __future__ import annotations

import json
import re

_REQUIRED_KEYS = ("root_cause", "suspected_files", "suspected_symbols")
_FENCE_RE = re.compile(r"^```(?:json)?\s*|\s*```$", re.DOTALL | re.MULTILINE)

JSON_SCHEMA = (
    "Respond with a JSON object only (no other text) matching this schema:\n"
    '{"root_cause": "<string>", "suspected_files": ["<filename>", ...], '
    '"suspected_symbols": ["<func_or_class>", ...], '
    '"confidence": "high"|"medium"|"low", "patch": "<optional diff>"}'
)


def parse_json_response(text: str) -> tuple[str, dict[str, object] | None]:
    """Parse LLM response as structured JSON.

    Strips markdown code fences if present, then validates required keys.

    Returns:
        (parser_status, parsed_dict | None).
        parser_status: 'parsed_ok' | 'parse_failed' | 'empty'.
    """
    stripped = text.strip()
    if not stripped:
        return "empty", None
    for candidate in (stripped, _FENCE_RE.sub("", stripped).strip()):
        try:
            data = json.loads(candidate)
            if all(k in data for k in _REQUIRED_KEYS):
                return "parsed_ok", data
            return "parse_failed", None
        except json.JSONDecodeError:
            continue
    return "parse_failed", None
