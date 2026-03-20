import pandas as pd
from pandas import DataFrame

from src.domain.contracts.load_strategy import BaseLoadStrategy


class IncrementalByDateStrategy(BaseLoadStrategy):
    def __init__(self, date_column: str):
        self.date_column = date_column

    @property
    def if_exists(self) -> str:
        return "append"

    def prepare(self, incoming_df: DataFrame, existing_df: DataFrame) -> DataFrame:
        if incoming_df.empty or existing_df.empty:
            return incoming_df

        incoming = incoming_df.copy()
        existing = existing_df.copy()

        incoming[self.date_column] = pd.to_datetime(incoming[self.date_column], errors="coerce")
        existing[self.date_column] = pd.to_datetime(existing[self.date_column], errors="coerce")

        max_existing_date = existing[self.date_column].max()
        if pd.isna(max_existing_date):
            return incoming

        return incoming[incoming[self.date_column] > max_existing_date]
