from __future__ import annotations

from abc import ABC, abstractmethod

from src.domain.models.ai_document import AIDocument
from src.domain.models.chunk import Chunk


class BaseChunker(ABC):
    @abstractmethod
    def chunk(self, document: AIDocument) -> list[Chunk]:
        raise NotImplementedError
