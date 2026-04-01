from __future__ import annotations

from src.application.ai.services.llm_service import LLMService
from src.application.ai.services.retrieval_service import RetrievalService
from src.domain.models.llm_response import LLMResponse


class RAGFlow:
    def __init__(self, retrieval_service: RetrievalService, llm_service: LLMService):
        self.retrieval_service = retrieval_service
        self.llm_service = llm_service

    def answer(self, question: str, top_k: int) -> LLMResponse:
        contexts = self.retrieval_service.search(query=question, top_k=top_k)
        return self.llm_service.answer(question=question, contexts=contexts)
