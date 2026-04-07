"""Domain contract for producing a final answer from a prompt + contexts."""

from __future__ import annotations

from abc import ABC, abstractmethod

from src.domain.models.llm_response import LLMResponse
from src.domain.models.retrieval_result import RetrievalResult


class BaseAnswerGenerator(ABC):
    """Answer generator interface (template/openai/etc.)."""

    @abstractmethod
    def generate(self, prompt: str, contexts: list[RetrievalResult]) -> LLMResponse:
        """Generate an LLM response for the given prompt and contexts."""
        raise NotImplementedError
