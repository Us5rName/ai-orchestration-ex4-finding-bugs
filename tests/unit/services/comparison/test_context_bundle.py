"""Tests for ContextBundle and related types."""

from __future__ import annotations

import pytest

from ex04.services.comparison.context_bundle import (
    ContextBundle,
    ContextProvenance,
    ContextStrategy,
    SourceRef,
)


def _bundle(content: str = "ctx", strategy: ContextStrategy = ContextStrategy.NAIVE) -> ContextBundle:
    prov = ContextProvenance(strategy=strategy, token_count=10, source_count=1)
    return ContextBundle(
        content=content,
        strategy=strategy,
        source_refs=(SourceRef(path="a.py", kind="file"),),
        provenance=prov,
    )


def test_context_bundle_is_immutable() -> None:
    b = _bundle()
    with pytest.raises(AttributeError):
        b.content = "other"  # type: ignore[misc]


def test_source_ref_is_immutable() -> None:
    r = SourceRef(path="x.py", kind="file")
    with pytest.raises(AttributeError):
        r.path = "y.py"  # type: ignore[misc]


def test_context_provenance_is_immutable() -> None:
    p = ContextProvenance(strategy=ContextStrategy.NAIVE, token_count=5, source_count=1)
    with pytest.raises(AttributeError):
        p.token_count = 99  # type: ignore[misc]


def test_strategy_values() -> None:
    assert ContextStrategy.NAIVE.value == "naive"
    assert ContextStrategy.GRAPH_GUIDED.value == "graph_guided"


def test_context_bundle_strategy_field_matches_provenance() -> None:
    b = _bundle(strategy=ContextStrategy.GRAPH_GUIDED)
    assert b.strategy == ContextStrategy.GRAPH_GUIDED
    assert b.provenance.strategy == ContextStrategy.GRAPH_GUIDED


def test_source_ref_optional_label() -> None:
    r = SourceRef(path="a.py", kind="node")
    assert r.label is None
    r2 = SourceRef(path="b.py", kind="node", label="MyClass")
    assert r2.label == "MyClass"


def test_source_refs_tuple_is_immutable() -> None:
    b = _bundle()
    with pytest.raises(TypeError):
        b.source_refs[0] = SourceRef(path="x.py", kind="file")  # type: ignore[index]


def test_empty_source_refs() -> None:
    prov = ContextProvenance(strategy=ContextStrategy.NAIVE, token_count=0, source_count=0)
    b = ContextBundle(
        content="",
        strategy=ContextStrategy.NAIVE,
        source_refs=(),
        provenance=prov,
    )
    assert b.source_refs == ()
