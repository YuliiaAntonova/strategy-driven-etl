"""Domain contract for loading dataframes into a target system."""

from abc import ABC, abstractmethod
from pandas import DataFrame


class BaseLoader(ABC):
    """Loader interface used by use cases/pipelines."""

    @abstractmethod
    def load(self, df: DataFrame, chunk_size: int | None = None) -> None:
        """Load DataFrame to target system."""
        raise NotImplementedError
