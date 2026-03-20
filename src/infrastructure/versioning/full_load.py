from pandas import DataFrame

from src.domain.contracts.load_strategy import BaseLoadStrategy


class FullLoadStrategy(BaseLoadStrategy):
    @property
    def if_exists(self) -> str:
        return "replace"

    def prepare(self, incoming_df: DataFrame, existing_df: DataFrame) -> DataFrame:
        return incoming_df
