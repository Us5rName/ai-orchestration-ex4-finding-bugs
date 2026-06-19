"""Config Manager — JSON config loading with dot-notation access.

Implements ConfigManagerInterface with JSON file loading, dot-notation
key access, and required-field validation.

All configuration values are externalized in config/setup.json per
[PRD NFR-4]. No hardcoded config values in source code.

## Contract (ConfigManagerInterface)

| Method | Input | Output | Phase |
|---|---|---|---|
| `load(path)` | str (JSON file path) | dict[str, Any] | P4 |
| `get(key_path)` | str (dot-notation) | Any | P4 |
| `validate(config)` | dict[str, Any] | bool | P4 |

## Required Fields

Top-level keys required for validity: `provider`, `agent`.

Implementation: **Phase 4** (T4.00)
"""

from __future__ import annotations

import json
from abc import ABC, abstractmethod
from pathlib import Path
from typing import Any


class ConfigManagerInterface(ABC):
    """Abstract configuration manager interface."""

    @abstractmethod
    def load(self, path: str) -> dict[str, Any]:
        """Load configuration from a JSON file and cache it."""

    @abstractmethod
    def get(self, key_path: str) -> Any:
        """Get a configuration value using dot-notation path."""

    @abstractmethod
    def validate(self, config: dict[str, Any]) -> bool:
        """Validate that a configuration dictionary has all required fields."""


class ConfigManager(ConfigManagerInterface):
    """JSON configuration manager with dot-notation access.

    Loads configuration from JSON files, caches it, and provides
    dot-notation access to nested values (e.g. 'agent.max_iterations').

    Attributes:
        _config: Cached configuration dictionary loaded from JSON.
        _required_keys: Top-level keys required for validity.
    """

    _required_keys: list[str] = ["provider", "agent"]

    def __init__(self) -> None:
        """Initialize with empty config cache."""
        self._config: dict[str, Any] = {}

    def load(self, path: str) -> dict[str, Any]:
        """Load configuration from a JSON file and cache it.

        Args:
            path: Path to the JSON configuration file.

        Returns:
            Parsed configuration dictionary.

        Raises:
            FileNotFoundError: If the configuration file does not exist.
            ValueError: If the JSON is malformed.
        """
        config_file = Path(path)
        if not config_file.exists():
            raise FileNotFoundError(f"Config file not found: {path}")

        try:
            raw = config_file.read_text(encoding="utf-8")
            self._config = json.loads(raw)
        except json.JSONDecodeError as exc:
            raise ValueError(f"Malformed JSON in {path}: {exc}") from exc

        return self._config

    def get(self, key_path: str) -> Any:
        """Get a configuration value using dot-notation path.

        Args:
            key_path: Dot-separated key path (e.g. 'provider.model').

        Returns:
            The configuration value at the given path.

        Raises:
            KeyError: If the key path does not exist.
            RuntimeError: If config has not been loaded yet.
        """
        if not self._config:
            raise RuntimeError("Config not loaded. Call load() first.")

        keys = key_path.split(".")
        current: Any = self._config

        for key in keys:
            if not isinstance(current, dict) or key not in current:
                raise KeyError(f"Key not found: {key_path}")
            current = current[key]

        return current

    def validate(self, config: dict[str, Any]) -> bool:
        """Validate that a configuration dictionary has all required fields.

        Args:
            config: Configuration dictionary to validate.

        Returns:
            True if the configuration is valid.

        Raises:
            ValueError: If required fields are missing.
        """
        missing = [key for key in self._required_keys if key not in config]
        if missing:
            raise ValueError(f"Missing required config keys: {missing}")
        return True
