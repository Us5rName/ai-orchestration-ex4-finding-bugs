"""Canonical prompt envelope for comparison experiments.

Both comparison modes (naive and graph-guided) must use this builder.
The system_prompt text comes from the ComparisonRequest so experiments
can vary the system prompt as a controlled field; the *structure* of
the prompt envelope (ordering, section labels, schema attachment) is
canonical and never duplicated in individual runners.
"""

from __future__ import annotations

from dataclasses import dataclass, field

from ex04.providers.interface import Message
from ex04.services.comparison._output_parser import JSON_SCHEMA
from ex04.services.comparison.context_bundle import ContextBundle

PROMPT_ENVELOPE_VERSION = "1.0"

_USER_TEMPLATE = (
    "{system_prompt}\nBug:\n{bug_report}\n\n{context_content}\n\n{schema}"
)


@dataclass(frozen=True, slots=True)
class ComparisonPromptInput:
    """All inputs required to build a canonical comparison prompt.

    Attributes:
        system_prompt: Controlled system instructions (from ComparisonRequest).
        bug_report: The bug report text.
        context_bundle: Strategy-produced context (the treatment variable).
        output_schema: Schema string appended to the user message.
    """

    system_prompt: str
    bug_report: str
    context_bundle: ContextBundle
    output_schema: str = field(default=JSON_SCHEMA)


class PromptBuilder:
    """Builds canonical comparison prompts for both runner modes.

    Both NaiveRunner and GraphGuidedRunner must use one shared instance
    of this class. The prompt structure is identical across modes; only
    the ContextBundle content and provenance differ.
    """

    VERSION: str = PROMPT_ENVELOPE_VERSION

    def build_messages(self, inp: ComparisonPromptInput) -> list[Message]:
        """Return the canonical message list for one comparison call.

        Args:
            inp: All prompt inputs including the context bundle.

        Returns:
            A single-element list with a user-role message whose content
            embeds the system instructions, bug report, context, and schema
            in canonical order.
        """
        content = _USER_TEMPLATE.format(
            system_prompt=inp.system_prompt,
            bug_report=inp.bug_report,
            context_content=inp.context_bundle.content,
            schema=inp.output_schema,
        )
        return [{"role": "user", "content": content}]
