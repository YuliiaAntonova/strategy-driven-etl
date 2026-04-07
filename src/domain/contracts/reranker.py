"""Domain contract for reranking retrieval results."""

from __future__ import annotations

from abc import ABC, abstractmethod

from src.domain.models.retrieval_result import RetrievalResult


class BaseReranker(ABC):
    """Reranker interface (keyword-metadata, cross-encoder, etc.)."""

    @abstractmethod
    def rerank(
        self,
        query: str,
        results: list[RetrievalResult],
        top_k: int,
    ) -> list[RetrievalResult]:
        """Return a reranked subset of results."""
        raise NotImplementedError
