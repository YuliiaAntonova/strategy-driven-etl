from __future__ import annotations

from src.application.ai.factory import get_ai_runtime
from src.application.ai.orchestration.rag_flow import RAGFlow
from src.application.ai.registry import LLM_PROVIDER_FACTORIES, RETRIEVER_FACTORIES
from src.application.ai.services.llm_service import LLMService
from src.application.ai.services.retrieval_service import RetrievalService
from src.config.settings import settings


def answer_query(question: str, profile: str | None = None, top_k: int | None = None, connector=None) -> str:
    runtime = get_ai_runtime(profile=profile, connector=connector)
    retriever = RETRIEVER_FACTORIES[runtime.ai_profile.retriever_key]()
    provider = LLM_PROVIDER_FACTORIES[runtime.ai_profile.llm_provider_key]()

    rag_flow = RAGFlow(
        retrieval_service=RetrievalService(repository=runtime.repository, retriever=retriever),
        llm_service=LLMService(provider=provider),
    )
    response = rag_flow.answer(question=question, top_k=top_k or settings.ai_top_k)
    return response.text
