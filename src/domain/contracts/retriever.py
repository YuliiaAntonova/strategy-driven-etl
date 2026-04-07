"""Domain contract for retrieving relevant chunks for a query."""

from __future__ import annotations

from abc import ABC, abstractmethod

from pandas import DataFrame

from src.domain.models.retrieval_result import RetrievalResult


class BaseRetriever(ABC):
    """Retriever interface (keyword/vector/etc.)."""

    @abstractmethod
    def retrieve(
        self,
        query: str,
        chunks_df: DataFrame,
        top_k: int,
    ) -> list[RetrievalResult]:
        """Return the top_k most relevant retrieval results."""
        raise NotImplementedError
