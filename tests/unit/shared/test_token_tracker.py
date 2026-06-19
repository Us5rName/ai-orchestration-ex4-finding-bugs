"""Tests for the Token Tracker interface contract — T2.05.

Verifies that TokenTrackerInterface is an abstract base class
with the required abstract methods. The actual implementation
will be provided in **Phase 6**.
"""

import inspect

import pytest

from ex04.shared.token_tracker import TokenTrackerInterface


def test_token_tracker_is_abstract():
    """TokenTrackerInterface should be an ABC."""
    assert inspect.isabstract(TokenTrackerInterface)


def test_token_tracker_cannot_be_instantiated():
    """TokenTrackerInterface cannot be instantiated directly."""
    with pytest.raises(TypeError):
        TokenTrackerInterface()


def test_token_tracker_has_record():
    """TokenTrackerInterface should have an abstract record method."""
    assert hasattr(TokenTrackerInterface, "record")


def test_token_tracker_has_total():
    """TokenTrackerInterface should have an abstract total method."""
    assert hasattr(TokenTrackerInterface, "total")


def test_token_tracker_has_by_session():
    """TokenTrackerInterface should have an abstract by_session method."""
    assert hasattr(TokenTrackerInterface, "by_session")


def test_token_tracker_has_export():
    """TokenTrackerInterface should have an abstract export method."""
    assert hasattr(TokenTrackerInterface, "export")


def test_token_tracker_record_signature():
    """TokenTrackerInterface.record should have correct signature."""
    sig = inspect.signature(TokenTrackerInterface.record)
    params = list(sig.parameters.keys())
    assert "self" in params
    assert "metrics" in params


def test_token_tracker_total_signature():
    """TokenTrackerInterface.total should have correct signature."""
    sig = inspect.signature(TokenTrackerInterface.total)
    params = list(sig.parameters.keys())
    assert "self" in params
    assert "provider" in params


def test_token_tracker_by_session_signature():
    """TokenTrackerInterface.by_session should have correct signature."""
    sig = inspect.signature(TokenTrackerInterface.by_session)
    params = list(sig.parameters.keys())
    assert "self" in params
    assert "session_id" in params


def test_token_tracker_concrete_impl_can_be_subclassed():
    """A concrete implementation should be instantiable."""

    class TestTokenTracker(TokenTrackerInterface):
        def record(self, metrics):
            pass

        def total(self, provider: str) -> int:
            return 0

        def by_session(self, session_id: str):
            return {}

        def export(self):
            return {}

    tracker = TestTokenTracker()
    tracker.record(None)
    assert tracker.total("openai") == 0
    assert tracker.by_session("s1") == {}
    assert tracker.export() == {}
