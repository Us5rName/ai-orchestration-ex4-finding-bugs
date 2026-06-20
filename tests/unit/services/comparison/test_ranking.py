"""Tests for bug-report-sensitive entity ranking."""

from __future__ import annotations

from ex04.services.comparison.ranking import extract_terms, rank_entities, score_entity
from ex04.shared.types import Entity, Relationship


def _entity(name: str, kind: str = "function", file_path: str = "buggy.py") -> Entity:
    return Entity(name=name, kind=kind, file_path=file_path, line_range=(1, 10))


def _rel(src: str, tgt: str) -> Relationship:
    return Relationship(source=src, target=tgt, type="calls")


def test_term_match_outranks_high_degree() -> None:
    """Entity whose name matches bug-report term ranks above a high-degree entity."""
    process = _entity("process_data")  # matches bug report
    helper = _entity("helper_utils")   # does not match

    # Give helper_utils high degree
    rels = [_rel("helper_utils", f"x{i}") for i in range(10)]
    ranked = rank_entities([process, helper], rels, "IndexError in process_data", max_count=5)

    names = [e.name for e, _ in ranked]
    assert names[0] == "process_data", f"Expected process_data first, got {names}"


def test_missing_anchor_does_not_raise() -> None:
    """Entity without file_path is included in ranking without raising."""
    e = Entity(name="mystery", kind="function", file_path="", line_range=(0, 0))
    ranked = rank_entities([e], [], "bug report", max_count=5)
    assert len(ranked) == 1
    assert ranked[0][0].name == "mystery"


def test_score_entity_term_hit_increases_score() -> None:
    """Entities whose name matches bug terms score higher than those that don't."""
    e_match = _entity("process_data")
    e_no_match = _entity("some_utility")
    terms = {"process", "data"}
    s_match = score_entity(e_match, terms, {}, 1)
    s_no_match = score_entity(e_no_match, terms, {}, 1)
    assert s_match > s_no_match


def test_rank_returns_at_most_max_count() -> None:
    entities = [_entity(f"func_{i}") for i in range(30)]
    ranked = rank_entities(entities, [], "test bug", max_count=10)
    assert len(ranked) <= 10


def test_extract_terms_filters_stop_words() -> None:
    terms = extract_terms("IndexError in the process_data function")
    assert "the" not in terms
    assert "indexerror" in terms
    assert "process_data" in terms
