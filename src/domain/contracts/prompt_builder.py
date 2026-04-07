"""Domain contract for building an LLM prompt from question + contexts."""

from __future__ import annotations

from abc import ABC, abstractmethod

from src.domain.models.retrieval_result import RetrievalResult


class BasePromptBuilder(ABC):
    """Prompt builder interface."""

    @abstractmethod
    def build(self, question: str, contexts: list[RetrievalResult]) -> str:
        """Create an LLM prompt string."""
        raise NotImplementedError
