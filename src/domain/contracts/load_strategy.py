from abc import ABC, abstractmethod
from pandas import DataFrame


class BaseLoadStrategy(ABC):
    @abstractmethod
    def prepare(self, incoming_df: DataFrame, existing_df: DataFrame) -> DataFrame:
        """Return the subset of incoming data that should be loaded."""
        raise NotImplementedError

    @property
    @abstractmethod
    def if_exists(self) -> str:
        """Return pandas.to_sql if_exists mode for this strategy."""
        raise NotImplementedError
