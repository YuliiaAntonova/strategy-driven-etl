from __future__ import annotations

from src.application.ai.profiles import AI_PROFILES
from src.application.ai.registry import (
    ANSWER_GENERATOR_FACTORIES,
    PROMPT_BUILDER_FACTORIES,
    RERANKER_FACTORIES,
    RETRIEVER_FACTORIES,
)
from src.application.ai.services.grounded_answer_service import GroundedAnswerService
from src.application.ai.services.reranking_service import RerankingService
from src.application.ai.services.retrieval_service import RetrievalService
from src.config.settings import settings
from src.infrastructure.ai.repositories.postgres_ai_repository import PostgresAIRepository
from src.infrastructure.connectors.postgres import PostgreSQLConnector


class GroundedAnswerServiceBuilder:
    @staticmethod
    def build(profile: str | None = None, connector=None) -> GroundedAnswerService:
        profile_name = profile or settings.ai_default_profile
        ai_profile = AI_PROFILES[profile_name]

        connector = connector or PostgreSQLConnector(
            host=settings.postgres_host,
            database=settings.postgres_db,
            user=settings.postgres_user,
            password=settings.postgres_password,
            port=settings.postgres_port,
        )

        repository = PostgresAIRepository(
            connector=connector,
            document_table=settings.ai_document_table,
            chunk_table=settings.ai_chunk_table,
        )
        retriever = RETRIEVER_FACTORIES[ai_profile.retriever_key]()
        reranker = RERANKER_FACTORIES[ai_profile.reranker_key]()
        prompt_builder = PROMPT_BUILDER_FACTORIES[ai_profile.prompt_builder_key]()
        answer_generator = ANSWER_GENERATOR_FACTORIES[ai_profile.answer_generator_key]()

        return GroundedAnswerService(
            retrieval_service=RetrievalService(repository=repository, retriever=retriever),
            reranking_service=RerankingService(reranker=reranker),
            prompt_builder=prompt_builder,
            answer_generator=answer_generator,
        )
