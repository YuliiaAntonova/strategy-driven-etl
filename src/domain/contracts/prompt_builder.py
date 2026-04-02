from __future__ import annotations

from abc import ABC, abstractmethod

from src.domain.models.retrieval_result import RetrievalResult


class BasePromptBuilder(ABC):
    @abstractmethod
    def build(self, question: str, contexts: list[RetrievalResult]) -> str:
        raise NotImplementedError
