"""Incremental load strategy based on a hash column.

Keeps only rows whose `hash_column` value does not exist in the current target
dataset.
"""

from pandas import DataFrame

from src.domain.contracts.load_strategy import BaseLoadStrategy


class IncrementalByHashStrategy(BaseLoadStrategy):
    """Append-only strategy: only load rows with previously unseen hashes."""

    def __init__(self, hash_column: str = "row_hash"):
        self.hash_column = hash_column

    @property
    def if_exists(self) -> str:
        return "append"

    def prepare(self, incoming_df: DataFrame, existing_df: DataFrame) -> DataFrame:
        """Filter `incoming_df` to hashes not present in `existing_df`."""
        if incoming_df.empty or existing_df.empty:
            return incoming_df

        existing_hashes = set(existing_df[self.hash_column].dropna().astype(str))
        incoming = incoming_df.copy()
        return incoming[
            ~incoming[self.hash_column].astype(str).isin(existing_hashes)
        ]
