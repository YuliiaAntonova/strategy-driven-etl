from pandas import DataFrame

from src.domain.contracts.load_strategy import BaseLoadStrategy


class IncrementalByHashStrategy(BaseLoadStrategy):
    def __init__(self, hash_column: str = "row_hash"):
        self.hash_column = hash_column

    @property
    def if_exists(self) -> str:
        return "append"

    def prepare(self, incoming_df: DataFrame, existing_df: DataFrame) -> DataFrame:
        if incoming_df.empty or existing_df.empty:
            return incoming_df

        existing_hashes = set(existing_df[self.hash_column].dropna().astype(str))
        incoming = incoming_df.copy()
        return incoming[~incoming[self.hash_column].astype(str).isin(existing_hashes)]
