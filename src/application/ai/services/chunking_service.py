from __future__ import annotations

import json

import pandas as pd
from pandas import DataFrame

from src.domain.contracts.chunker import BaseChunker
from src.domain.models.ai_document import AIDocument


class ChunkingService:
    def __init__(self, chunker: BaseChunker):
        self.chunker = chunker

    def chunk_documents(self, documents_df: DataFrame) -> DataFrame:
        rows: list[dict[str, str | int]] = []
        if documents_df.empty:
            return pd.DataFrame(columns=[
                "chunk_id", "document_id", "entity_id", "position", "content", "metadata_json"
            ])

        for _, row in documents_df.iterrows():
            metadata = json.loads(row.get("metadata_json", "{}") or "{}")
            document = AIDocument(
                document_id=str(row["document_id"]),
                entity_id=str(row["entity_id"]),
                source_type=str(row.get("source_type", "job")),
                title=str(row.get("title", row["document_id"])),
                content=str(row.get("content", "")),
                metadata=metadata,
            )
            for chunk in self.chunker.chunk(document):
                rows.append({
                    "chunk_id": chunk.chunk_id,
                    "document_id": chunk.document_id,
                    "entity_id": chunk.entity_id,
                    "position": chunk.position,
                    "content": chunk.content,
                    "metadata_json": json.dumps(chunk.metadata, ensure_ascii=False),
                })

        return pd.DataFrame(rows)
