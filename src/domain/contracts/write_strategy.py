from abc import ABC, abstractmethod
from pandas import DataFrame


class BaseWriteStrategy(ABC):
    @abstractmethod
    def write(self, df: DataFrame, chunk_size: int | None = None) -> None:
        pass