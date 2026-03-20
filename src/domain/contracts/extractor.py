from abc import ABC, abstractmethod

from pandas import DataFrame


class BaseExtractor(ABC):
    @abstractmethod
    def extract(self) -> DataFrame:
        """Return source data as a pandas DataFrame."""
        raise NotImplementedError
