"""Domain contract for persisting and retrieving AI indexing artifacts."""

from __future__ import annotations

from abc import ABC, abstractmethod

from pandas import DataFrame


class BaseAIRepository(ABC):
    """Repository interface for AI documents/chunks storage."""

    @abstractmethod
    def replace_documents(self, documents_df: DataFrame) -> None:
        """Replace all AI documents with the provided dataframe."""
        raise NotImplementedError

    @abstractmethod
    def replace_chunks(self, chunks_df: DataFrame) -> None:
        """Replace all AI chunks with the provided dataframe."""
        raise NotImplementedError

    @abstractmethod
    def read_chunks(self) -> DataFrame:
        """Read chunks (and related metadata) for retrieval/reranking."""
        raise NotImplementedError
