"""Tests for ConfigManager.validate() and integration — T4.00."""

from __future__ import annotations

from pathlib import Path

import pytest

from ex04.shared.config import ConfigManager


class TestConfigManagerValidate:
    """Tests for ConfigManager.validate() method."""

    def test_validate_complete_config(self) -> None:
        config = {
            "project": {"name": "ex04", "version": "1.00"},
            "provider": {"name": "openai", "model": "gpt-4o-mini"},
            "agent": {"max_iterations": 5},
        }
        manager = ConfigManager()
        assert manager.validate(config) is True

    def test_validate_empty_config(self) -> None:
        manager = ConfigManager()
        with pytest.raises(ValueError):
            manager.validate({})

    def test_validate_missing_required_field(self) -> None:
        config = {"provider": {"name": "openai"}}
        manager = ConfigManager()
        with pytest.raises(ValueError):
            manager.validate(config)


class TestConfigManagerIntegration:
    """Integration tests using actual config/setup.json."""

    def test_load_actual_config(self) -> None:
        config_path = Path(__file__).parent.parent.parent.parent / "config" / "setup.json"
        if not config_path.exists():
            pytest.skip("config/setup.json not found")

        manager = ConfigManager()
        result = manager.load(str(config_path))
        assert "provider" in result
        assert "agent" in result

    def test_get_from_actual_config(self) -> None:
        config_path = Path(__file__).parent.parent.parent.parent / "config" / "setup.json"
        if not config_path.exists():
            pytest.skip("config/setup.json not found")

        manager = ConfigManager()
        manager.load(str(config_path))
        assert manager.get("provider.name") == "openai"
        assert manager.get("agent.max_iterations") == 5
