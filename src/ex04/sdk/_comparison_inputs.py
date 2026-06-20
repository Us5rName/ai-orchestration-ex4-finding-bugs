"""Shared helper for deterministic comparison input preparation.

Discovers eligible Python source files from a target codebase directory,
applies exclusion rules, enforces configured limits, and sorts results
deterministically.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any

def resolve_vault_dir(vault: dict[str, "Path"]) -> "Path | None":
    """Resolve the vault directory from a built vault artifact map.

    Prefers the parent of the 'index' note (canonical artifact), then the
    parent of the first available note. Returns None when vault is empty.
    """
    if not vault:
        return None
    if "index" in vault:
        return vault["index"].parent
    return next(iter(vault.values())).parent


_EXCLUDED_DIRS = frozenset(
    {
        ".git",
        ".venv",
        "venv",
        "env",
        "__pycache__",
        ".mypy_cache",
        ".pytest_cache",
        ".ruff_cache",
        "build",
        "dist",
        "site-packages",
        "node_modules",
    }
)


def discover_source_files(
    target_path: Path | str,
    config: dict[str, Any] | None = None,
) -> list[Path]:
    """Discover eligible Python source files in a target codebase.

    Recursively walks the target directory, excludes generated/vendor/cache
    directories, sorts results deterministically, and optionally limits the
    count via ``config["comparison"]["naive_file_limit"]``.

    Args:
        target_path: Root directory of the target codebase.
        config: Optional loaded SDK config dict; used to read naive_file_limit.

    Returns:
        Sorted list of eligible Python source file paths.

    Raises:
        FileNotFoundError: If the target path does not exist.
        NotADirectoryError: If the target path is not a directory.
        FileNotFoundError: If no eligible Python files are found.
    """
    target = Path(target_path)
    if not target.exists():
        raise FileNotFoundError(f"Target path does not exist: {target}")
    if not target.is_dir():
        raise NotADirectoryError(f"Target path is not a directory: {target}")

    files: list[Path] = sorted(
        path
        for path in target.rglob("*.py")
        if not any(part in _EXCLUDED_DIRS for part in path.parts)
    )

    if not files:
        raise FileNotFoundError(f"No eligible Python source files found in: {target}")

    limit = _parse_limit(config)
    if limit is not None:
        files = files[:limit]

    return files


def _parse_limit(config: dict[str, Any] | None) -> int | None:
    """Extract and validate naive_file_limit from config.

    Args:
        config: Optional config dict.

    Returns:
        Positive integer limit, or None if not configured.

    Raises:
        ValueError: If the configured limit is invalid (not positive int).
    """
    if config is None:
        return None
    raw = config.get("comparison", {}).get("naive_file_limit")
    if raw is None:
        return None
    try:
        limit = int(raw)
    except (TypeError, ValueError) as exc:
        raise ValueError(f"Invalid naive_file_limit: {raw!r}") from exc
    if limit < 1:
        raise ValueError(f"naive_file_limit must be a positive integer, got {limit}")
    return limit
