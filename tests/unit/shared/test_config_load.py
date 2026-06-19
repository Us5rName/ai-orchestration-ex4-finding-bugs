"""Tests for ConfigManager.load() — T4.00."""

from __future__ import annotations

import json
import os
import tempfile

import pytest

from ex04.shared.config import ConfigManager


class TestConfigManagerLoad:
    """Tests for ConfigManager.load() method."""

    def test_load_valid_config(self) -> None:
        with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as tmp:
            json.dump({"key": "value", "nested": {"a": 1}}, tmp)
            tmp_path = tmp.name

        try:
            manager = ConfigManager()
            result = manager.load(tmp_path)
            assert result == {"key": "value", "nested": {"a": 1}}
        finally:
            os.unlink(tmp_path)

    def test_load_caches_config(self) -> None:
        with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as tmp:
            json.dump({"provider": {"name": "openai"}}, tmp)
            tmp_path = tmp.name

        try:
            manager = ConfigManager()
            manager.load(tmp_path)
            assert manager._config == {"provider": {"name": "openai"}}
        finally:
            os.unlink(tmp_path)

    def test_load_file_not_found(self) -> None:
        manager = ConfigManager()
        with pytest.raises(FileNotFoundError):
            manager.load("/nonexistent/path/config.json")

    def test_load_malformed_json(self) -> None:
        with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as tmp:
            tmp.write("{invalid json}")
            tmp_path = tmp.name

        try:
            manager = ConfigManager()
            with pytest.raises(ValueError):
                manager.load(tmp_path)
        finally:
            os.unlink(tmp_path)
