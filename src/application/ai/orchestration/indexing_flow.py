from __future__ import annotations

from pandas import DataFrame

from src.application.ai.services.chunking_service import ChunkingService
from src.application.ai.services.document_service import DocumentService
from src.application.ai.services.embedding_service import EmbeddingService
from src.domain.contracts.ai_repository import BaseAIRepository


class AIIndexingFlow:
    def __init__(
        self,
        document_service: DocumentService,
        chunking_service: ChunkingService,
        embedding_service: EmbeddingService,
        repository: BaseAIRepository,
    ):
        self.document_service = document_service
        self.chunking_service = chunking_service
        self.embedding_service = embedding_service
        self.repository = repository

    def run(self, jobs_df: DataFrame) -> tuple[DataFrame, DataFrame]:
        documents_df = self.document_service.build_from_jobs(jobs_df)
        chunks_df = self.chunking_service.chunk_documents(documents_df)
        embedded_chunks_df = self.embedding_service.add_embeddings(chunks_df)
        self.repository.replace_documents(documents_df)
        self.repository.replace_chunks(embedded_chunks_df)
        return documents_df, embedded_chunks_df
