from __future__ import annotations

from src.application.ai.orchestration.rag_flow import RAGFlow
from src.application.ai.profiles import AI_PROFILES
from src.application.ai.registry import LLM_PROVIDER_FACTORIES, RETRIEVER_FACTORIES
from src.application.ai.services.llm_service import LLMService
from src.application.ai.services.retrieval_service import RetrievalService
from src.config.settings import settings
from src.infrastructure.ai.repositories.postgres_ai_repository import PostgresAIRepository
from src.infrastructure.connectors.postgres import PostgreSQLConnector


def answer_query(question: str, profile: str | None = None, top_k: int | None = None, connector=None) -> str:
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
    provider = LLM_PROVIDER_FACTORIES[ai_profile.llm_provider_key]()

    rag_flow = RAGFlow(
        retrieval_service=RetrievalService(repository=repository, retriever=retriever),
        llm_service=LLMService(provider=provider),
    )
    response = rag_flow.answer(question=question, top_k=top_k or settings.ai_top_k)
    return response.text
