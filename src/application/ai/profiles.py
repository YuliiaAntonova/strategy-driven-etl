from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class AIProfile:
    name: str
    chunker_key: str
    embedder_key: str
    retriever_key: str
    llm_provider_key: str


AI_PROFILES: dict[str, AIProfile] = {
    "jobs_rag_local": AIProfile(
        name="jobs_rag_local",
        chunker_key="recursive",
        embedder_key="token_frequency",
        retriever_key="keyword",
        llm_provider_key="template",
    ),
}
