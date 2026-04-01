from __future__ import annotations

from src.application.ai.orchestration.indexing_flow import AIIndexingFlow
from src.application.ai.profiles import AI_PROFILES
from src.application.ai.registry import CHUNKER_FACTORIES, EMBEDDER_FACTORIES
from src.application.ai.services.chunking_service import ChunkingService
from src.application.ai.services.document_service import DocumentService
from src.application.ai.services.embedding_service import EmbeddingService
from src.config.settings import settings
from src.infrastructure.ai.repositories.postgres_ai_repository import PostgresAIRepository
from src.infrastructure.connectors.postgres import PostgreSQLConnector
from src.infrastructure.extractors.postgres import PostgresExtractor


def run_ai_indexing(profile: str | None = None, connector=None) -> None:
    profile_name = profile or settings.ai_default_profile
    ai_profile = AI_PROFILES[profile_name]

    connector = connector or PostgreSQLConnector(
        host=settings.postgres_host,
        database=settings.postgres_db,
        user=settings.postgres_user,
        password=settings.postgres_password,
        port=settings.postgres_port,
    )

    jobs_df = PostgresExtractor(
        connector=connector,
        query=f"select * from {settings.target_table} where is_current = true",
    ).extract()

    chunker = CHUNKER_FACTORIES[ai_profile.chunker_key](settings.ai_chunk_size, settings.ai_chunk_overlap)
    embedder = EMBEDDER_FACTORIES[ai_profile.embedder_key]()
    repository = PostgresAIRepository(
        connector=connector,
        document_table=settings.ai_document_table,
        chunk_table=settings.ai_chunk_table,
    )

    flow = AIIndexingFlow(
        document_service=DocumentService(
            content_columns=settings.ai_document_columns,
            metadata_columns=settings.ai_metadata_columns,
        ),
        chunking_service=ChunkingService(chunker),
        embedding_service=EmbeddingService(embedder),
        repository=repository,
    )
    documents_df, chunks_df = flow.run(jobs_df)
    print(
        f"AI indexing completed with {len(documents_df)} documents and {len(chunks_df)} chunks "
        f"using profile '{profile_name}'"
    )
