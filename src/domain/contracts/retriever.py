from __future__ import annotations

from abc import ABC, abstractmethod

from pandas import DataFrame

from src.domain.models.retrieval_result import RetrievalResult


class BaseRetriever(ABC):
    @abstractmethod
    def retrieve(self, query: str, chunks_df: DataFrame, top_k: int) -> list[RetrievalResult]:
        raise NotImplementedError
