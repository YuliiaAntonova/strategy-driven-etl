from __future__ import annotations

from src.application.ai.factory import get_ai_runtime
from src.application.ai.orchestration.indexing_flow import AIIndexingFlow
from src.application.ai.registry import CHUNKER_FACTORIES, EMBEDDER_FACTORIES
from src.application.ai.services.chunking_service import ChunkingService
from src.application.ai.services.document_service import DocumentService
from src.application.ai.services.embedding_service import EmbeddingService
from src.config.settings import settings
from src.infrastructure.extractors.postgres import PostgresExtractor


def run_ai_indexing(profile: str | None = None, connector=None) -> dict[str, int | str]:
    runtime = get_ai_runtime(profile=profile, connector=connector)

    jobs_df = PostgresExtractor(
        connector=runtime.connector,
        query=f"select * from {settings.target_table} where is_current = true",
    ).extract()

    chunker = CHUNKER_FACTORIES[runtime.ai_profile.chunker_key](settings.ai_chunk_size, settings.ai_chunk_overlap)
    embedder = EMBEDDER_FACTORIES[runtime.ai_profile.embedder_key]()

    flow = AIIndexingFlow(
        document_service=DocumentService(
            content_columns=settings.ai_document_columns,
            metadata_columns=settings.ai_metadata_columns,
        ),
        chunking_service=ChunkingService(chunker),
        embedding_service=EmbeddingService(embedder),
        repository=runtime.repository,
    )
    documents_df, chunks_df = flow.run(jobs_df)
    summary = {
        "profile": runtime.profile_name,
        "documents_count": int(len(documents_df)),
        "chunks_count": int(len(chunks_df)),
    }
    print(
        f"AI indexing completed with {summary['documents_count']} documents and {summary['chunks_count']} chunks "
        f"using profile '{runtime.profile_name}'"
    )
    return summary
