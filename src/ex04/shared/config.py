"""Config Manager interface — contract for configuration loading.

This module defines the abstract interface that all configuration managers
must implement. The actual implementation will be provided in **Phase 4**
when services require configuration access.

## Contract

| Method | Input | Output | Phase |
|---|---|---|---|
| `load(path)` | str (JSON file path) | dict[str, Any] | P4 |
| `get(key_path)` | str (dot-notation) | Any | P4 |
| `validate(config)` | dict[str, Any] | bool | P4 |

## Usage

```python
from ex04.shared.config import ConfigManagerInterface

class MyConfigManager(ConfigManagerInterface):
    def load(self, path: str) -> dict: ...
    def get(self, key_path: str) -> Any: ...
    def validate(self, config: dict) -> bool: ...
```

Actual implementation: **Phase 4** (services need config to function).
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any


class ConfigManagerInterface(ABC):
    """Abstract configuration manager interface.

    All configuration managers must implement these methods to ensure
    consistent configuration access across the system.

    Attributes:
        _config: Cached configuration dictionary loaded from JSON.
    """

    @abstractmethod
    def load(self, path: str) -> dict[str, Any]:
        """Load configuration from a JSON file.

        Args:
            path: Path to the JSON configuration file.

        Returns:
            Parsed configuration dictionary.

        Raises:
            FileNotFoundError: If the configuration file does not exist.
            ValueError: If the JSON is malformed or missing required fields.
        """

    @abstractmethod
    def get(self, key_path: str) -> Any:
        """Get a configuration value using dot-notation path.

        Supports nested access like 'provider.name' or 'agent.max_iterations'.

        Args:
            key_path: Dot-separated key path (e.g. 'provider.model').

        Returns:
            The configuration value at the given path.

        Raises:
            KeyError: If the key path does not exist in the configuration.
        """

    @abstractmethod
    def validate(self, config: dict[str, Any]) -> bool:
        """Validate that a configuration dictionary has all required fields.

        Args:
            config: Configuration dictionary to validate.

        Returns:
            True if the configuration is valid.

        Raises:
            ValueError: If required fields are missing or invalid.
        """
