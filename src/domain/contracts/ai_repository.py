from __future__ import annotations

from abc import ABC, abstractmethod

from pandas import DataFrame


class BaseAIRepository(ABC):
    @abstractmethod
    def replace_documents(self, documents_df: DataFrame) -> None:
        raise NotImplementedError

    @abstractmethod
    def replace_chunks(self, chunks_df: DataFrame) -> None:
        raise NotImplementedError

    @abstractmethod
    def read_chunks(self) -> DataFrame:
        raise NotImplementedError
