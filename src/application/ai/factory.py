"""Factories for wiring AI/RAG runtime dependencies.

This module centralizes creation of:
- the selected AI profile
- the Postgres connector
- the AI repository

Keeping this wiring in one place reduces duplication across use cases.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, TypeAlias

from src.application.ai.profiles import AI_PROFILES
from src.config.settings import settings
from src.infrastructure.ai.repositories.postgres_ai_repository import PostgresAIRepository
from src.infrastructure.connectors.factory import get_postgres_connector


AIProfile: TypeAlias = Any


@dataclass(frozen=True)
class AIRuntime:
    """Resolved runtime wiring for AI flows."""

    profile_name: str
    ai_profile: AIProfile
    connector: Any
    repository: PostgresAIRepository


def get_ai_profile(profile: str | None = None) -> tuple[str, AIProfile]:
    """Return the resolved profile name and its configuration object."""

    profile_name = profile or settings.ai_default_profile
    return profile_name, AI_PROFILES[profile_name]


def get_ai_repository(connector: Any = None) -> PostgresAIRepository:
    """Create a Postgres-backed AI repository using a resolved connector."""

    resolved_connector = get_postgres_connector(connector)
    return PostgresAIRepository(
        connector=resolved_connector,
        document_table=settings.ai_document_table,
        chunk_table=settings.ai_chunk_table,
    )


def get_ai_runtime(profile: str | None = None, connector: Any = None) -> AIRuntime:
    """Build an `AIRuntime` object for downstream AI use cases."""

    profile_name, ai_profile = get_ai_profile(profile)
    resolved_connector = get_postgres_connector(connector)
    repository = get_ai_repository(resolved_connector)
    return AIRuntime(
        profile_name=profile_name,
        ai_profile=ai_profile,
        connector=resolved_connector,
        repository=repository,
    )
