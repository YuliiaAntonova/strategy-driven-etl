import pandas as pd
from pandas import DataFrame

from src.domain.contracts.load_strategy import BaseLoadStrategy
from src.infrastructure.versioning.frame_utils import (
    latest_rows_by_primary_key,
    normalize_existing_versioned_frame,
    normalize_incoming_versioned_frame,
    prepare_changed_versioned_row,
    prepare_new_versioned_row,
)


class IncrementalByPrimaryKeyAndHashStrategy(BaseLoadStrategy):
    def __init__(self, primary_key: str, hash_column: str = "row_hash"):
        self.primary_key = primary_key
        self.hash_column = hash_column

    @property
    def if_exists(self) -> str:
        return "append"

    def prepare(self, incoming_df: DataFrame, existing_df: DataFrame) -> DataFrame:
        if incoming_df.empty:
            return incoming_df

        if self.primary_key not in incoming_df.columns:
            raise ValueError(f"Primary key column '{self.primary_key}' not found in incoming data")
        if self.hash_column not in incoming_df.columns:
            raise ValueError(f"Hash column '{self.hash_column}' not found in incoming data")

        incoming = normalize_incoming_versioned_frame(incoming_df)

        if existing_df.empty:
            return incoming.apply(prepare_new_versioned_row, axis=1)

        if self.primary_key not in existing_df.columns:
            raise ValueError(f"Primary key column '{self.primary_key}' not found in existing data")
        if self.hash_column not in existing_df.columns:
            raise ValueError(
                f"Hash column '{self.hash_column}' not found in existing data. Run full load first."
            )

        existing = normalize_existing_versioned_frame(existing_df)
        existing_latest = latest_rows_by_primary_key(existing, self.primary_key)

        existing_hash_map = existing_latest.set_index(self.primary_key)[self.hash_column].to_dict()
        existing_created_map = existing_latest.set_index(self.primary_key)["date_created"].to_dict()

        rows = []
        for _, row in incoming.iterrows():
            key = row[self.primary_key]
            row_hash = row[self.hash_column]

            if key not in existing_hash_map:
                rows.append(prepare_new_versioned_row(row))
                continue

            if existing_hash_map[key] == row_hash:
                continue

            existing_created = existing_created_map.get(key)
            rows.append(prepare_changed_versioned_row(row, existing_created))

        if not rows:
            return incoming.iloc[0:0].copy()

        return DataFrame(rows).reset_index(drop=True)
