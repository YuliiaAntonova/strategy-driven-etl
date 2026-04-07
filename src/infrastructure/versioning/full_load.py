"""Full load strategy.

Replaces the target table contents with the incoming dataset.
"""

from pandas import DataFrame

from src.domain.contracts.load_strategy import BaseLoadStrategy


class FullLoadStrategy(BaseLoadStrategy):
    """Load strategy that always writes the full incoming dataset."""

    @property
    def if_exists(self) -> str:
        return "replace"

    def prepare(self, incoming_df: DataFrame, existing_df: DataFrame) -> DataFrame:
        """Return the full `incoming_df` unchanged."""
        return incoming_df
