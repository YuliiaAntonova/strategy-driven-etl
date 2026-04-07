"""Domain model for responses returned by an LLM provider.

This model is kept deliberately small and provider-agnostic.
"""

from __future__ import annotations

from dataclasses import dataclass, field


@dataclass(frozen=True)
class LLMResponse:
    """Textual LLM output plus optional metadata (model, tokens, etc.)."""

    text: str
    metadata: dict[str, str] = field(default_factory=dict)
