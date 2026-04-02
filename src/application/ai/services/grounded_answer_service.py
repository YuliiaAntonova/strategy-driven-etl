from __future__ import annotations

from src.application.ai.services.retrieval_service import RetrievalService
from src.application.ai.services.reranking_service import RerankingService
from src.domain.contracts.answer_generator import BaseAnswerGenerator
from src.domain.contracts.prompt_builder import BasePromptBuilder
from src.domain.models.answer_result import AnswerResult


class GroundedAnswerService:
    def __init__(
        self,
        retrieval_service: RetrievalService,
        reranking_service: RerankingService,
        prompt_builder: BasePromptBuilder,
        answer_generator: BaseAnswerGenerator,
    ):
        self.retrieval_service = retrieval_service
        self.reranking_service = reranking_service
        self.prompt_builder = prompt_builder
        self.answer_generator = answer_generator

    def answer(self, question: str, fetch_k: int, top_k: int) -> AnswerResult:
        retrieved = self.retrieval_service.search(query=question, top_k=fetch_k)
        contexts = self.reranking_service.rerank(query=question, results=retrieved, top_k=top_k)
        prompt = self.prompt_builder.build(question=question, contexts=contexts)
        response = self.answer_generator.generate(prompt=prompt, contexts=contexts)
        return AnswerResult(text=response.text, contexts=contexts, metadata=response.metadata)
