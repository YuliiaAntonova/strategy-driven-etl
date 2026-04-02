from __future__ import annotations

from abc import ABC, abstractmethod

from src.domain.models.retrieval_result import RetrievalResult


class BaseReranker(ABC):
    @abstractmethod
    def rerank(self, query: str, results: list[RetrievalResult], top_k: int) -> list[RetrievalResult]:
        raise NotImplementedError
