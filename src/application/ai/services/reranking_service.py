from __future__ import annotations

from src.domain.contracts.reranker import BaseReranker
from src.domain.models.retrieval_result import RetrievalResult


class RerankingService:
    def __init__(self, reranker: BaseReranker):
        self.reranker = reranker

    def rerank(self, query: str, results: list[RetrievalResult], top_k: int) -> list[RetrievalResult]:
        return self.reranker.rerank(query=query, results=results, top_k=top_k)
