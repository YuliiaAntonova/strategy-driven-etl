"""Domain contract for extracting source data as a dataframe."""

from abc import ABC, abstractmethod

from pandas import DataFrame


class BaseExtractor(ABC):
    """Extractor interface (CSV/Postgres/API/etc.)."""

    @abstractmethod
    def extract(self) -> DataFrame:
        """Return source data as a pandas DataFrame."""
        raise NotImplementedError
