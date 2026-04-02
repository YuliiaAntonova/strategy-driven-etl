from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class AIProfile:
    name: str
    chunker_key: str
    embedder_key: str
    retriever_key: str
    llm_provider_key: str
    reranker_key: str = "keyword_metadata"
    prompt_builder_key: str = "grounded"
    answer_generator_key: str = "template"


AI_PROFILES: dict[str, AIProfile] = {
    "jobs_rag_local": AIProfile(
        name="jobs_rag_local",
        chunker_key="recursive",
        embedder_key="token_frequency",
        retriever_key="keyword",
        llm_provider_key="template",
        reranker_key="keyword_metadata",
        prompt_builder_key="grounded",
        answer_generator_key="template",
    ),
    "jobs_rag_openai": AIProfile(
        name="jobs_rag_openai",
        chunker_key="recursive",
        embedder_key="token_frequency",
        retriever_key="keyword",
        llm_provider_key="template",
        reranker_key="keyword_metadata",
        prompt_builder_key="grounded",
        answer_generator_key="openai",
    ),
}
