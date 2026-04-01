from __future__ import annotations

from abc import ABC, abstractmethod

from src.domain.models.llm_response import LLMResponse
from src.domain.models.retrieval_result import RetrievalResult


class BaseLLMProvider(ABC):
    @abstractmethod
    def generate(self, question: str, contexts: list[RetrievalResult]) -> LLMResponse:
        raise NotImplementedError
