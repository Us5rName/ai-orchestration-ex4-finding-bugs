"""Tests for the API Gatekeeper interface contract — T2.04.

Verifies that GatekeeperInterface is an abstract base class
with the required abstract methods. The actual implementation
will be provided in **Phase 4**.
"""

import inspect

import pytest

from ex04.shared.gatekeeper import GatekeeperInterface


def test_gatekeeper_is_abstract():
    """GatekeeperInterface should be an ABC."""
    assert inspect.isabstract(GatekeeperInterface)


def test_gatekeeper_cannot_be_instantiated():
    """GatekeeperInterface cannot be instantiated directly."""
    with pytest.raises(TypeError):
        GatekeeperInterface()


def test_gatekeeper_has_send():
    """GatekeeperInterface should have an abstract send method."""
    assert hasattr(GatekeeperInterface, "send")


def test_gatekeeper_has_get_call_log():
    """GatekeeperInterface should have an abstract get_call_log method."""
    assert hasattr(GatekeeperInterface, "get_call_log")


def test_gatekeeper_has_get_queue_status():
    """GatekeeperInterface should have an abstract get_queue_status method."""
    assert hasattr(GatekeeperInterface, "get_queue_status")


def test_gatekeeper_send_signature():
    """GatekeeperInterface.send should have correct signature."""
    sig = inspect.signature(GatekeeperInterface.send)
    params = list(sig.parameters.keys())
    assert "self" in params
    assert "provider" in params
    assert "messages" in params


def test_gatekeeper_concrete_impl_can_be_subclassed():
    """A concrete implementation should be instantiable."""

    class TestGatekeeper(GatekeeperInterface):
        def send(self, provider: str, messages: list[dict[str, str]]):
            return {"content": "mock", "input_tokens": 0, "output_tokens": 0}

        def get_call_log(self):
            return []

        def get_queue_status(self):
            return {"queue_size": 0, "is_processing": False, "rate_limited": False}

    gatekeeper = TestGatekeeper()
    result = gatekeeper.send("openai", [{"role": "user", "content": "hi"}])
    assert result["content"] == "mock"
    assert gatekeeper.get_call_log() == []
    assert gatekeeper.get_queue_status()["queue_size"] == 0
