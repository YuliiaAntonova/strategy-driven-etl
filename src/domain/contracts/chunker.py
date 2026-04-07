"""Domain contract for splitting a document into retrievable chunks."""

from __future__ import annotations

from abc import ABC, abstractmethod

from src.domain.models.ai_document import AIDocument
from src.domain.models.chunk import Chunk


class BaseChunker(ABC):
    """Chunker interface used during AI indexing."""

    @abstractmethod
    def chunk(self, document: AIDocument) -> list[Chunk]:
        """Split a document into chunks."""
        raise NotImplementedError
