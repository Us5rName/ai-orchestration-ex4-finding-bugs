"""Tests for ConfigManager.get() — T4.00."""

from __future__ import annotations

import json
import os
import tempfile

import pytest

from ex04.shared.config import ConfigManager


class TestConfigManagerGet:
    """Tests for ConfigManager.get() method."""

    def test_get_flat_key(self) -> None:
        with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as tmp:
            json.dump({"name": "ex04", "version": "1.00"}, tmp)
            tmp_path = tmp.name

        try:
            manager = ConfigManager()
            manager.load(tmp_path)
            assert manager.get("name") == "ex04"
            assert manager.get("version") == "1.00"
        finally:
            os.unlink(tmp_path)

    def test_get_nested_key_dot_notation(self) -> None:
        with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as tmp:
            json.dump({"provider": {"name": "openai", "model": "gpt-4o-mini"}}, tmp)
            tmp_path = tmp.name

        try:
            manager = ConfigManager()
            manager.load(tmp_path)
            assert manager.get("provider.name") == "openai"
            assert manager.get("provider.model") == "gpt-4o-mini"
        finally:
            os.unlink(tmp_path)

    def test_get_deeply_nested_key(self) -> None:
        with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as tmp:
            json.dump({"a": {"b": {"c": {"d": "deep_value"}}}}, tmp)
            tmp_path = tmp.name

        try:
            manager = ConfigManager()
            manager.load(tmp_path)
            assert manager.get("a.b.c.d") == "deep_value"
        finally:
            os.unlink(tmp_path)

    def test_get_missing_key_raises_keyerror(self) -> None:
        with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as tmp:
            json.dump({"existing": "value"}, tmp)
            tmp_path = tmp.name

        try:
            manager = ConfigManager()
            manager.load(tmp_path)
            with pytest.raises(KeyError):
                manager.get("nonexistent")
        finally:
            os.unlink(tmp_path)

    def test_get_missing_nested_key_raises_keyerror(self) -> None:
        with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as tmp:
            json.dump({"provider": {"name": "openai"}}, tmp)
            tmp_path = tmp.name

        try:
            manager = ConfigManager()
            manager.load(tmp_path)
            with pytest.raises(KeyError):
                manager.get("provider.missing_key")
        finally:
            os.unlink(tmp_path)

    def test_get_returns_none_for_null_values(self) -> None:
        with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as tmp:
            json.dump({"provider": {"base_url": None}}, tmp)
            tmp_path = tmp.name

        try:
            manager = ConfigManager()
            manager.load(tmp_path)
            assert manager.get("provider.base_url") is None
        finally:
            os.unlink(tmp_path)
