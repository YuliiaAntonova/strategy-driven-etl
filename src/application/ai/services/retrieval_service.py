from __future__ import annotations

from src.domain.contracts.ai_repository import BaseAIRepository
from src.domain.contracts.retriever import BaseRetriever
from src.domain.models.retrieval_result import RetrievalResult


class RetrievalService:
    def __init__(self, repository: BaseAIRepository, retriever: BaseRetriever):
        self.repository = repository
        self.retriever = retriever

    def search(self, query: str, top_k: int) -> list[RetrievalResult]:
        chunks_df = self.repository.read_chunks()
        return self.retriever.retrieve(query=query, chunks_df=chunks_df, top_k=top_k)
