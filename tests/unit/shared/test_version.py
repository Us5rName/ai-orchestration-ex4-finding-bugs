"""Tests for the version module — T2.01.

Verifies that the global version string is correctly defined
and follows the expected MAJOR.MINOR format.
"""

from ex04.shared import __version__


def test_version_is_string():
    """Version should be a string."""
    assert isinstance(__version__, str)


def test_version_format():
    """Version should follow MAJOR.MINOR format."""
    parts = __version__.split(".")
    assert len(parts) == 2, f"Expected MAJOR.MINOR format, got '{__version__}'"
    assert parts[0].isdigit(), f"Major version should be numeric, got '{parts[0]}'"
    assert parts[1].isdigit(), f"Minor version should be numeric, got '{parts[1]}'"


def test_version_value():
    """Version should start at 1.00."""
    assert __version__ == "1.00"
