from abc import ABC, abstractmethod

from pandas import DataFrame


class BaseLoader(ABC):
    @abstractmethod
    def load(self, df: DataFrame) -> None:
        """Load DataFrame to target system."""
        raise NotImplementedError
