from __future__ import annotations

from dataclasses import dataclass, field

from src.domain.models.retrieval_result import RetrievalResult


@dataclass(frozen=True)
class AnswerResult:
    text: str
    contexts: list[RetrievalResult] = field(default_factory=list)
    metadata: dict[str, str] = field(default_factory=dict)
