from __future__ import annotations

from src.application.ai.factory import get_ai_runtime
from src.application.ai.registry import (
    ANSWER_GENERATOR_FACTORIES,
    PROMPT_BUILDER_FACTORIES,
    RERANKER_FACTORIES,
    RETRIEVER_FACTORIES,
)
from src.application.ai.services.grounded_answer_service import GroundedAnswerService
from src.application.ai.services.reranking_service import RerankingService
from src.application.ai.services.retrieval_service import RetrievalService


class GroundedAnswerServiceBuilder:
    @staticmethod
    def build(profile: str | None = None, connector=None) -> GroundedAnswerService:
        runtime = get_ai_runtime(profile=profile, connector=connector)
        retriever = RETRIEVER_FACTORIES[runtime.ai_profile.retriever_key]()
        reranker = RERANKER_FACTORIES[runtime.ai_profile.reranker_key]()
        prompt_builder = PROMPT_BUILDER_FACTORIES[runtime.ai_profile.prompt_builder_key]()
        answer_generator = ANSWER_GENERATOR_FACTORIES[runtime.ai_profile.answer_generator_key]()

        return GroundedAnswerService(
            retrieval_service=RetrievalService(repository=runtime.repository, retriever=retriever),
            reranking_service=RerankingService(reranker=reranker),
            prompt_builder=prompt_builder,
            answer_generator=answer_generator,
        )
