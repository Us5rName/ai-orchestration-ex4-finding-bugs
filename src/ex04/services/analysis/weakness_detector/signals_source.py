"""AST-aware source weakness signals."""

from __future__ import annotations

import ast
import hashlib
from collections import defaultdict

from ex04.services.analysis.weakness_detector.config import WeaknessConfig
from ex04.services.analysis.weakness_detector.models import (
    EvidenceAnchor,
    EvidenceConfidence,
    SourceValidation,
    ValidationStatus,
    WeaknessFinding,
    WeaknessSignal,
)
from ex04.services.analysis.weakness_detector.source_index import SourceIndex
from ex04.services.analysis.weakness_detector.utils import finding
from ex04.services.graph.interface import GraphReaderInterface


def semantic_duplicate_signal(
    *, reader: GraphReaderInterface, source_index: SourceIndex, config: WeaknessConfig
) -> tuple[WeaknessFinding, ...]:
    """Detect structurally equivalent Python definitions using ast."""
    if config.duplicate_strategy == "disabled":
        return ()
    buckets: dict[str, list[tuple[str, str, int, int]]] = defaultdict(list)
    validations: list[SourceValidation] = []
    for node in reader.all_nodes():
        if not node.file_path.endswith(".py"):
            continue
        parsed, validation = source_index.parse_ast(node.file_path)
        validations.append(validation)
        if parsed is None:
            continue
        for definition in _definitions(parsed):
            normalized = _normalize_def(definition)
            buckets[_digest(normalized)].append(
                (node.file_path, definition.name, definition.lineno, definition.end_lineno or definition.lineno)
            )
    findings = []
    for digest, defs in sorted(buckets.items()):
        unique = sorted(set(defs))
        if len(unique) < 2:
            continue
        anchors = tuple(EvidenceAnchor(path, start, end, name) for path, name, start, end in unique)
        findings.append(finding(
            signal=WeaknessSignal.SEMANTIC_DUPLICATE,
            tag=digest,
            score=0.7,
            summary=f"{len(unique)} Python definitions have equivalent normalized AST structure.",
            entity_ids=tuple(name for _, name, _, _ in unique),
            evidence=anchors,
            confidence=EvidenceConfidence.INFERRED,
            limitations=("Structural AST similarity is not proof of semantic equivalence.",),
            boundaries=config.severity_boundaries,
        ))
    if not findings and any(v.status is ValidationStatus.SYNTAX_ERROR for v in validations):
        return ()
    return tuple(findings)


def _definitions(tree: ast.AST) -> tuple[ast.FunctionDef | ast.AsyncFunctionDef | ast.ClassDef, ...]:
    return tuple(
        node for node in ast.walk(tree)
        if isinstance(node, ast.FunctionDef | ast.AsyncFunctionDef | ast.ClassDef)
    )


def _normalize_def(node: ast.AST) -> str:
    clone = _NameNormalizer().visit(node)
    ast.fix_missing_locations(clone)
    return ast.dump(clone, include_attributes=False)


def _digest(value: str) -> str:
    return hashlib.sha256(value.encode("utf-8")).hexdigest()[:16]


class _NameNormalizer(ast.NodeTransformer):
    """Normalize definition and variable names while preserving AST structure."""

    def visit_FunctionDef(self, node: ast.FunctionDef) -> ast.AST:
        node.name = "_"
        self.generic_visit(node)
        return node

    def visit_AsyncFunctionDef(self, node: ast.AsyncFunctionDef) -> ast.AST:
        node.name = "_"
        self.generic_visit(node)
        return node

    def visit_ClassDef(self, node: ast.ClassDef) -> ast.AST:
        node.name = "_"
        self.generic_visit(node)
        return node

    def visit_arg(self, node: ast.arg) -> ast.AST:
        node.arg = "_"
        return node

    def visit_Name(self, node: ast.Name) -> ast.AST:
        node.id = "_"
        return node

    def visit_Constant(self, node: ast.Constant) -> ast.AST:
        if isinstance(node.value, str):
            node.value = "_str"
        return node
