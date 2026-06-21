"""ArtifactStore — immutable evidence lifecycle management.

Implements overwrite protection, provenance recording, and sanitization.
Traceability: [PRD-AP], [TODO T7.09], [TODO T6.07]
"""

from __future__ import annotations

import hashlib
import json
import re
from dataclasses import asdict
from pathlib import Path

from ex04.shared.types_experiment import RunManifest

_SENSITIVE_PATTERNS = [
    re.compile(
        r"(?i)(api[_-]?key|secret|password|auth[_-]?token|access[_-]?token|refresh[_-]?token)"
    ),
    re.compile(r"/home/[^/]+"),
    re.compile(r"/Users/[^/]+"),
]


class ArtifactOverwriteError(RuntimeError):
    """Raised when attempting to overwrite an existing run artifact."""


class ArtifactStore:
    """Manages the immutable artifact directory structure.

    All run evidence is write-once: an existing run_id directory cannot
    be overwritten. Sanitizer strips sensitive keys and personal paths.
    """

    def __init__(self, artifacts_root: Path) -> None:
        """Initialize with the root artifacts directory."""
        self._root = artifacts_root
        self._manifests_dir = artifacts_root / "manifests"
        self._runs_dir = artifacts_root / "runs"

    def _ensure_dirs(self) -> None:
        """Create subdirectories on first use."""
        self._manifests_dir.mkdir(parents=True, exist_ok=True)
        self._runs_dir.mkdir(parents=True, exist_ok=True)

    def save_manifest(self, manifest: RunManifest) -> Path:
        """Persist a run manifest. Raises ArtifactOverwriteError if run_id exists."""
        self._ensure_dirs()
        run_dir = self._runs_dir / manifest.run_id
        path = self._manifests_dir / f"{manifest.run_id}_manifest.json"
        if path.exists():
            raise ArtifactOverwriteError(
                f"Manifest '{manifest.run_id}' already exists at {path}"
            )
        run_dir.mkdir(parents=True, exist_ok=True)
        data = sanitize_artifact(asdict(manifest))
        path.write_text(json.dumps(data, indent=2, default=str), encoding="utf-8")
        return path

    def load_manifest(self, run_id: str) -> dict[str, object]:
        """Load a previously saved manifest by run ID."""
        path = self._manifests_dir / f"{run_id}_manifest.json"
        if not path.exists():
            raise FileNotFoundError(f"Manifest not found: {path}")
        return json.loads(path.read_text(encoding="utf-8"))

    def list_runs(self) -> list[str]:
        """Return sorted list of existing run IDs."""
        if not self._runs_dir.exists():
            return []
        return sorted(p.name for p in self._runs_dir.iterdir() if p.is_dir())

    @staticmethod
    def config_hash(config: dict[str, object]) -> str:
        """Compute a stable SHA-256 hash of a config dict."""
        serialized = json.dumps(config, sort_keys=True, default=str)
        return hashlib.sha256(serialized.encode()).hexdigest()


def sanitize_artifact(data: dict[str, object]) -> dict[str, object]:
    """Remove sensitive keys and personal paths from artifact data.

    Recursively processes nested dicts. Sensitive keys and values matching
    personal path patterns are replaced with '<redacted>'.
    """
    if not isinstance(data, dict):
        return data
    result: dict[str, object] = {}
    for k, v in data.items():
        if any(p.search(str(k)) for p in _SENSITIVE_PATTERNS):
            result[k] = "<redacted>"
        elif isinstance(v, dict):
            result[k] = sanitize_artifact(v)
        elif isinstance(v, str) and any(p.search(v) for p in _SENSITIVE_PATTERNS):
            result[k] = "<redacted>"
        else:
            result[k] = v
    return result
