from pathlib import Path

from ex04.sdk.sdk import Ex04SDK
from ex04.services.analysis.weakness_detector import (
    WeaknessConfig,
    WeaknessDetector,
    WeaknessSignal,
)
from ex04.services.analysis.weakness_detector.models import ValidationStatus
from ex04.services.analysis.weakness_detector.source_index import SourceIndex
from ex04.shared.types import Entity, GraphData


def test_semantic_duplicate_uses_ast_and_line_anchors(tmp_path: Path) -> None:
    source = tmp_path / "sample.py"
    source.write_text(
        """
def first(value):
    # ignored comment
    return {"name": "alpha", "count": value + 1}

def second(item):
    return {'name': "beta", 'count': item + 1}

def different(value):
    return value - 1
""",
        encoding="utf-8",
    )
    data = GraphData(entities=[Entity("module", file_path="sample.py")])
    report = WeaknessDetector(WeaknessConfig(), source_root=tmp_path).detect(data)
    duplicate = [f for f in report.findings if f.signal is WeaknessSignal.SEMANTIC_DUPLICATE]
    assert len(duplicate) == 1
    assert duplicate[0].evidence[0].start_line == 2
    assert duplicate[0].confidence.value == "inferred"


def test_same_name_with_different_behavior_is_not_duplicate(tmp_path: Path) -> None:
    source = tmp_path / "sample.py"
    source.write_text(
        """
def same(value):
    return value + 1

def same_again(value):
    return value - 1
""",
        encoding="utf-8",
    )
    data = GraphData(entities=[Entity("module", file_path="sample.py")])
    report = WeaknessDetector(WeaknessConfig(), source_root=tmp_path).detect(data)
    assert not [f for f in report.findings if f.signal is WeaknessSignal.SEMANTIC_DUPLICATE]


def test_missing_and_malformed_source_do_not_fabricate_duplicates(tmp_path: Path) -> None:
    bad = tmp_path / "bad.py"
    bad.write_text("def broken(:\n", encoding="utf-8")
    data = GraphData(entities=[Entity("bad", file_path="bad.py"), Entity("missing", file_path="x.py")])
    report = WeaknessDetector(WeaknessConfig(), source_root=tmp_path).detect(data)
    assert not [f for f in report.findings if f.signal is WeaknessSignal.SEMANTIC_DUPLICATE]


def test_source_index_rejects_paths_outside_root(tmp_path: Path) -> None:
    index = SourceIndex(tmp_path)
    text, validation = index.read_text("../outside.py")
    assert text == ""
    assert validation.status is ValidationStatus.ERROR


def test_detect_weaknesses_sdk_operation_is_keyless_and_deterministic(tmp_path: Path) -> None:
    source = tmp_path / "sample.py"
    source.write_text(
        """
def one(x):
    return x + 1

def two(y):
    return y + 1
""",
        encoding="utf-8",
    )
    sdk = Ex04SDK(object(), object(), object(), object(), object())
    data = GraphData(entities=[Entity("module", file_path="sample.py")])
    first = sdk.detect_weaknesses(data, WeaknessConfig(), tmp_path)
    second = sdk.detect_weaknesses(data, WeaknessConfig(), tmp_path)
    assert first == second
    assert [f.signal for f in first.findings] == [
        WeaknessSignal.ISOLATED_COMPONENT,
        WeaknessSignal.SEMANTIC_DUPLICATE,
    ]
