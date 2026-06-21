"""Bounded source access for weakness signals."""

from __future__ import annotations

import ast
from pathlib import Path

from ex04.services.analysis.weakness_detector.models import SourceValidation, ValidationStatus


class SourceIndex:
    """Path-safe source reader with text and AST caches."""

    def __init__(self, root: Path | None = None, max_bytes: int = 262_144) -> None:
        self._root = root.resolve() if root else None
        self._max_bytes = max_bytes
        self._text_cache: dict[str, tuple[str, SourceValidation]] = {}
        self._ast_cache: dict[str, tuple[ast.AST | None, SourceValidation]] = {}

    def read_text(self, file_path: str) -> tuple[str, SourceValidation]:
        """Read a relative source file once, enforcing root and byte limits."""
        if file_path in self._text_cache:
            return self._text_cache[file_path]
        path, validation = self._resolve(file_path)
        if validation.status is not ValidationStatus.VALID or path is None:
            self._text_cache[file_path] = ("", validation)
            return self._text_cache[file_path]
        data = path.read_bytes()
        if len(data) > self._max_bytes:
            result = ("", SourceValidation(ValidationStatus.ERROR, "source read limit exceeded"))
        else:
            result = (data.decode("utf-8"), SourceValidation(ValidationStatus.VALID, file_path))
        self._text_cache[file_path] = result
        return result

    def parse_ast(self, file_path: str) -> tuple[ast.AST | None, SourceValidation]:
        """Parse a source file once with Python ast."""
        if file_path in self._ast_cache:
            return self._ast_cache[file_path]
        text, validation = self.read_text(file_path)
        if validation.status is not ValidationStatus.VALID:
            self._ast_cache[file_path] = (None, validation)
            return self._ast_cache[file_path]
        try:
            parsed = ast.parse(text, filename=file_path)
            result: tuple[ast.AST | None, SourceValidation] = (parsed, validation)
        except SyntaxError as exc:
            result = (None, SourceValidation(ValidationStatus.SYNTAX_ERROR, str(exc)))
        self._ast_cache[file_path] = result
        return result

    def _resolve(self, file_path: str) -> tuple[Path | None, SourceValidation]:
        if not file_path:
            return None, SourceValidation(ValidationStatus.MISSING, "missing source path")
        path = Path(file_path)
        if path.is_absolute():
            return None, SourceValidation(ValidationStatus.ERROR, "absolute paths are not allowed")
        resolved = (self._root / path).resolve() if self._root else path.resolve()
        if self._root and self._root not in (resolved, *resolved.parents):
            return None, SourceValidation(ValidationStatus.ERROR, "path escapes source root")
        if not resolved.exists():
            return None, SourceValidation(ValidationStatus.MISSING, f"source not found: {file_path}")
        return resolved, SourceValidation(ValidationStatus.VALID, file_path)
