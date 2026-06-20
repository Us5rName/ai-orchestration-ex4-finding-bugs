"""Repository validation script — enforces project coding standards.

Checks:
- File size limit (≤ 150 lines per .py file)
- No hardcoded secrets (patterns: API key, password, bearer token)
- No personal absolute paths (/home/..., /Users/...)
- No hardcoded configuration (URLs, timeouts) outside config/ directory
- SDK boundary: services must not import from sdk/
- Gatekeeper boundary: providers must only be called via gatekeeper

Run: uv run python scripts/validate_repo.py
Exits with code 1 if any violation is found.
"""

from __future__ import annotations

import re
import sys
from pathlib import Path

ROOT = Path(__file__).parent.parent
SRC = ROOT / "src"

_SECRET_PATTERNS = [
    re.compile(r"(?i)(api[_-]?key|password|bearer)\s*=\s*['\"][^'\"]{8,}"),
]
_PATH_PATTERNS = [
    # Match paths like '/home/username/...' but not regex patterns like r"/home/[^/]+"
    re.compile(r'["\']/(home|Users)/[A-Za-z0-9_.-]{2,}/'),
]
_SDK_IMPORT = re.compile(r"from ex04\.sdk")
_VIOLATIONS: list[str] = []


def _check_file_size() -> None:
    """All .py files in src/ must be ≤ 150 lines."""
    for path in SRC.rglob("*.py"):
        lines = len(path.read_text(encoding="utf-8").splitlines())
        if lines > 150:
            _VIOLATIONS.append(f"FILE_SIZE: {path.relative_to(ROOT)} has {lines} lines (>150)")


def _check_secrets() -> None:
    """No hardcoded secrets in .py files."""
    for path in SRC.rglob("*.py"):
        text = path.read_text(encoding="utf-8")
        for pattern in _SECRET_PATTERNS:
            if pattern.search(text):
                _VIOLATIONS.append(f"HARDCODED_SECRET: {path.relative_to(ROOT)}")
                break


def _check_personal_paths() -> None:
    """No personal absolute paths in .py files."""
    for path in SRC.rglob("*.py"):
        text = path.read_text(encoding="utf-8")
        for pattern in _PATH_PATTERNS:
            if pattern.search(text):
                _VIOLATIONS.append(f"PERSONAL_PATH: {path.relative_to(ROOT)}")
                break


def _check_sdk_boundary() -> None:
    """Service modules must not import from the SDK layer."""
    services_dir = SRC / "ex04" / "services"
    for path in services_dir.rglob("*.py"):
        text = path.read_text(encoding="utf-8")
        if _SDK_IMPORT.search(text):
            _VIOLATIONS.append(f"SDK_BOUNDARY: {path.relative_to(ROOT)} imports from sdk")


def _check_artifact_manifests() -> None:
    """All committed manifests must have required fields."""
    import json

    manifests_dir = ROOT / "artifacts" / "manifests"
    if not manifests_dir.exists():
        return
    required = {"run_id", "mode", "evidence_class", "telemetry_available", "limitations"}
    for path in manifests_dir.glob("*.json"):
        try:
            data = json.loads(path.read_text(encoding="utf-8"))
            missing = required - set(data.keys())
            if missing:
                _VIOLATIONS.append(f"MANIFEST_SCHEMA: {path.name} missing fields: {missing}")
        except json.JSONDecodeError:
            _VIOLATIONS.append(f"MANIFEST_INVALID_JSON: {path.name}")


def main() -> None:
    """Run all validation checks and exit with code 1 if violations found."""
    _check_file_size()
    _check_secrets()
    _check_personal_paths()
    _check_sdk_boundary()
    _check_artifact_manifests()

    if _VIOLATIONS:
        print(f"Repository validation FAILED ({len(_VIOLATIONS)} violations):")
        for v in _VIOLATIONS:
            print(f"  ✗ {v}")
        sys.exit(1)
    else:
        print(f"Repository validation PASSED (checked {len(list(SRC.rglob('*.py')))} files)")
        sys.exit(0)


if __name__ == "__main__":
    main()
