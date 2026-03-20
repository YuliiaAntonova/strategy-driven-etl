import pandas as pd
from pandas import DataFrame

from src.domain.contracts.load_strategy import BaseLoadStrategy


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

        incoming = incoming_df.copy()
        incoming["date_created"] = pd.to_datetime(incoming.get("date_created"), errors="coerce", utc=True)
        incoming["date_loaded"] = pd.to_datetime(incoming.get("date_loaded"), errors="coerce", utc=True)
        if "is_current" not in incoming.columns:
            incoming["is_current"] = True

        if existing_df.empty:
            incoming["date_created"] = incoming["date_created"].fillna(incoming["date_loaded"])
            return incoming

        if self.primary_key not in existing_df.columns:
            raise ValueError(f"Primary key column '{self.primary_key}' not found in existing data")
        if self.hash_column not in existing_df.columns:
            raise ValueError(
                f"Hash column '{self.hash_column}' not found in existing data. Run full load first."
            )

        existing = existing_df.copy()
        existing["date_created"] = pd.to_datetime(existing.get("date_created"), errors="coerce", utc=True)
        existing["date_loaded"] = pd.to_datetime(existing.get("date_loaded"), errors="coerce", utc=True)

        if "is_current" in existing.columns:
            existing = existing[existing["is_current"] == True].copy()

        existing_latest = (
            existing.sort_values(by="date_loaded", ascending=True, na_position="last")
            .dropna(subset=[self.primary_key])
            .drop_duplicates(subset=[self.primary_key], keep="last")
        )

        existing_hash_map = existing_latest.set_index(self.primary_key)[self.hash_column].to_dict()
        existing_created_map = existing_latest.set_index(self.primary_key)["date_created"].to_dict()

        rows = []
        for _, row in incoming.iterrows():
            key = row[self.primary_key]
            row_hash = row[self.hash_column]

            if key not in existing_hash_map:
                row = row.copy()
                row["date_created"] = row["date_created"] if pd.notna(row["date_created"]) else row["date_loaded"]
                row["is_current"] = True
                rows.append(row)
                continue

            if existing_hash_map[key] == row_hash:
                continue

            row = row.copy()
            existing_created = existing_created_map.get(key)
            row["date_created"] = existing_created if pd.notna(existing_created) else row["date_loaded"]
            row["is_current"] = True
            rows.append(row)

        if not rows:
            return incoming.iloc[0:0].copy()

        return DataFrame(rows).reset_index(drop=True)
