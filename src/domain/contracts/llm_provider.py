"""Domain contract for LLM providers used in grounded generation flows."""

from __future__ import annotations

from abc import ABC, abstractmethod

from src.domain.models.llm_response import LLMResponse
from src.domain.models.retrieval_result import RetrievalResult


class BaseLLMProvider(ABC):
    """LLM provider interface (template/openai/etc.)."""

    @abstractmethod
    def generate(self, question: str, contexts: list[RetrievalResult]) -> LLMResponse:
        """Generate an LLM response for the given question and contexts."""
        raise NotImplementedError
