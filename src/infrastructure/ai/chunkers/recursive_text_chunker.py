from __future__ import annotations

from src.domain.contracts.chunker import BaseChunker
from src.domain.models.ai_document import AIDocument
from src.domain.models.chunk import Chunk


class RecursiveTextChunker(BaseChunker):
    def __init__(self, chunk_size: int = 900, chunk_overlap: int = 120):
        if chunk_overlap >= chunk_size:
            raise ValueError("chunk_overlap must be smaller than chunk_size")
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap

    def chunk(self, document: AIDocument) -> list[Chunk]:
        text = document.content.strip()
        if not text:
            return []

        chunks: list[Chunk] = []
        start = 0
        position = 0
        while start < len(text):
            end = min(len(text), start + self.chunk_size)
            slice_text = text[start:end].strip()
            if slice_text:
                chunks.append(
                    Chunk(
                        chunk_id=f"{document.document_id}:{position}",
                        document_id=document.document_id,
                        entity_id=document.entity_id,
                        position=position,
                        content=slice_text,
                        metadata=document.metadata | {"title": document.title},
                    )
                )
                position += 1
            if end >= len(text):
                break
            start = max(0, end - self.chunk_overlap)
        return chunks
