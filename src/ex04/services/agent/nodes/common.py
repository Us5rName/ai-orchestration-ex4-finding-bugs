"""Shared helpers for agent LangGraph nodes."""

from __future__ import annotations

import re
from pathlib import Path
from typing import Any

from ex04.shared.gatekeeper import GatekeeperInterface
from ex04.shared.types_metrics import TokenMetrics
from ex04.shared.types_results import ProviderResponse, Suspect

_SUSPECT_RE = re.compile(r"(?P<file>[\w./-]+\.py):(?P<start>\d+)(?:-(?P<end>\d+))?")


def call_gatekeeper(
    gatekeeper: GatekeeperInterface | None,
    provider: str,
    prompt: str,
) -> ProviderResponse:
    """Call the configured gatekeeper or return an offline placeholder."""
    if gatekeeper is None:
        return ProviderResponse(text="", provider=provider)
    return gatekeeper.send(provider, [{"role": "user", "content": prompt}])


def merge_tokens(state: dict[str, Any], response: ProviderResponse) -> TokenMetrics:
    """Merge response token counts into state token usage."""
    current = state.get("token_usage", TokenMetrics())
    return TokenMetrics(
        input_tokens=current.input_tokens + response.input_tokens,
        output_tokens=current.output_tokens + response.output_tokens,
        total_tokens=current.total_tokens + response.input_tokens + response.output_tokens,
        provider=response.provider or current.provider,
        model=response.model or current.model,
    )


def parse_suspects(text: str) -> list[Suspect]:
    """Parse file:line-line references from model text into suspects."""
    suspects: list[Suspect] = []
    for match in _SUSPECT_RE.finditer(text):
        start = int(match.group("start"))
        end = int(match.group("end") or start)
        suspects.append(
            Suspect(
                file_path=match.group("file"),
                line_start=start,
                line_end=end,
                score=1.0,
                reason=text[max(match.start() - 40, 0) : match.end() + 80].strip(),
            )
        )
    return suspects


def read_path_context(path_text: str, max_chars: int) -> str:
    """Read a file or markdown directory context, bounded by max_chars."""
    path = Path(path_text)
    if path.is_file():
        return path.read_text(encoding="utf-8")[:max_chars]
    if not path.is_dir():
        return path_text[:max_chars]
    parts: list[str] = []
    for note in sorted(path.rglob("*.md")):
        content = note.read_text(encoding="utf-8")
        parts.append(f"--- {note.relative_to(path)} ---\n{content}")
        if sum(len(part) for part in parts) >= max_chars:
            break
    return "\n".join(parts)[:max_chars]
