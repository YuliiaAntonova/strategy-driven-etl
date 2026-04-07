"""Domain contract for transforming dataframes."""

from abc import ABC, abstractmethod

from pandas import DataFrame


class BaseTransformer(ABC):
    """Transformer interface applied during ETL."""

    @abstractmethod
    def transform(self, df: DataFrame) -> DataFrame:
        """Transform input DataFrame and return transformed DataFrame."""
        raise NotImplementedError
