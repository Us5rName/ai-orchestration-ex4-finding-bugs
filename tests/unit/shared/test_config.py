"""Tests for the Config Manager interface contract — T2.03.

Verifies that ConfigManagerInterface is an abstract base class
with the required abstract methods. The actual implementation
will be provided in **Phase 4**.
"""

import inspect

import pytest

from ex04.shared.config import ConfigManagerInterface


def test_config_manager_is_abstract():
    """ConfigManagerInterface should be an ABC."""
    assert inspect.isabstract(ConfigManagerInterface)


def test_config_manager_cannot_be_instantiated():
    """ConfigManagerInterface cannot be instantiated directly."""
    with pytest.raises(TypeError):
        ConfigManagerInterface()


def test_config_manager_has_load():
    """ConfigManagerInterface should have an abstract load method."""
    assert hasattr(ConfigManagerInterface, "load")
    assert inspect.isabstract(ConfigManagerInterface.load) or hasattr(
        ConfigManagerInterface.load, "__isabstractmethod__"
    )


def test_config_manager_has_get():
    """ConfigManagerInterface should have an abstract get method."""
    assert hasattr(ConfigManagerInterface, "get")
    assert inspect.isabstract(ConfigManagerInterface.get) or hasattr(
        ConfigManagerInterface.get, "__isabstractmethod__"
    )


def test_config_manager_has_validate():
    """ConfigManagerInterface should have an abstract validate method."""
    assert hasattr(ConfigManagerInterface, "validate")
    assert inspect.isabstract(ConfigManagerInterface.validate) or hasattr(
        ConfigManagerInterface.validate, "__isabstractmethod__"
    )


def test_config_manager_load_signature():
    """ConfigManagerInterface.load should have correct signature."""
    sig = inspect.signature(ConfigManagerInterface.load)
    params = list(sig.parameters.keys())
    assert "self" in params
    assert "path" in params


def test_config_manager_get_signature():
    """ConfigManagerInterface.get should have correct signature."""
    sig = inspect.signature(ConfigManagerInterface.get)
    params = list(sig.parameters.keys())
    assert "self" in params
    assert "key_path" in params


def test_config_manager_validate_signature():
    """ConfigManagerInterface.validate should have correct signature."""
    sig = inspect.signature(ConfigManagerInterface.validate)
    params = list(sig.parameters.keys())
    assert "self" in params
    assert "config" in params


def test_concrete_impl_can_be_subclassed():
    """A concrete implementation should be instantiable."""

    class TestConfigManager(ConfigManagerInterface):
        def load(self, path: str) -> dict:
            return {}

        def get(self, key_path: str):
            return None

        def validate(self, config: dict) -> bool:
            return True

    manager = TestConfigManager()
    assert manager.load("fake.json") == {}
    assert manager.get("a.b") is None
    assert manager.validate({"a": 1}) is True
