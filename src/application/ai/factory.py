from __future__ import annotations

from dataclasses import dataclass

from src.application.ai.profiles import AI_PROFILES
from src.config.settings import settings
from src.infrastructure.ai.repositories.postgres_ai_repository import PostgresAIRepository
from src.infrastructure.connectors.factory import get_postgres_connector


@dataclass(frozen=True)
class AIRuntime:
    profile_name: str
    ai_profile: object
    connector: object
    repository: PostgresAIRepository


def get_ai_profile(profile: str | None = None):
    profile_name = profile or settings.ai_default_profile
    return profile_name, AI_PROFILES[profile_name]


def get_ai_repository(connector=None) -> PostgresAIRepository:
    resolved_connector = get_postgres_connector(connector)
    return PostgresAIRepository(
        connector=resolved_connector,
        document_table=settings.ai_document_table,
        chunk_table=settings.ai_chunk_table,
    )


def get_ai_runtime(profile: str | None = None, connector=None) -> AIRuntime:
    profile_name, ai_profile = get_ai_profile(profile)
    resolved_connector = get_postgres_connector(connector)
    repository = get_ai_repository(resolved_connector)
    return AIRuntime(
        profile_name=profile_name,
        ai_profile=ai_profile,
        connector=resolved_connector,
        repository=repository,
    )
