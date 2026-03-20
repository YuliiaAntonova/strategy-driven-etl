from pandas import DataFrame

from src.domain.contracts.load_strategy import BaseLoadStrategy


class IncrementalByPrimaryKeyStrategy(BaseLoadStrategy):
    def __init__(self, primary_key: str):
        self.primary_key = primary_key

    @property
    def if_exists(self) -> str:
        return "append"

    def prepare(self, incoming_df: DataFrame, existing_df: DataFrame) -> DataFrame:
        if incoming_df.empty or existing_df.empty:
            return incoming_df

        existing_keys = set(existing_df[self.primary_key].dropna().astype(str))
        incoming = incoming_df.copy()
        return incoming[~incoming[self.primary_key].astype(str).isin(existing_keys)]
