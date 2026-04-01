from __future__ import annotations

import pandas as pd
from pandas import DataFrame

from src.domain.models.change_set import ChangeSet


class BaseTabularChangeDetector:
    def __init__(self, primary_key: str | None = None, hash_column: str = "row_hash"):
        self.primary_key = primary_key
        self.hash_column = hash_column

    def _classify_candidates(self, candidates_df: DataFrame, existing_df: DataFrame) -> ChangeSet:
        if candidates_df.empty:
            return ChangeSet.empty_like(candidates_df)

        if not self.primary_key:
            empty = candidates_df.iloc[0:0].copy()
            return ChangeSet(new_rows=candidates_df.reset_index(drop=True), changed_rows=empty.copy(), unchanged_rows=empty.copy())

        if self.primary_key not in candidates_df.columns:
            raise ValueError(f"Primary key column '{self.primary_key}' not found in incoming data")
        if self.hash_column not in candidates_df.columns:
            raise ValueError(f"Hash column '{self.hash_column}' not found in incoming data")

        incoming = candidates_df.copy()
        incoming["date_created"] = pd.to_datetime(incoming.get("date_created"), errors="coerce", utc=True)
        incoming["date_loaded"] = pd.to_datetime(incoming.get("date_loaded"), errors="coerce", utc=True)
        if "is_current" not in incoming.columns:
            incoming["is_current"] = True

        if existing_df.empty:
            new_rows = incoming.copy()
            new_rows["date_created"] = new_rows["date_created"].fillna(new_rows["date_loaded"])
            new_rows["is_current"] = True
            return ChangeSet(
                new_rows=new_rows.reset_index(drop=True),
                changed_rows=incoming.iloc[0:0].copy(),
                unchanged_rows=incoming.iloc[0:0].copy(),
            )

        existing = existing_df.copy()
        existing["date_created"] = pd.to_datetime(existing.get("date_created"), errors="coerce", utc=True)
        existing["date_loaded"] = pd.to_datetime(existing.get("date_loaded"), errors="coerce", utc=True)
        if "is_current" in existing.columns:
            existing = existing[existing["is_current"] == True].copy()

        if self.primary_key not in existing.columns or self.hash_column not in existing.columns:
            new_rows = incoming.copy()
            new_rows["date_created"] = new_rows["date_created"].fillna(new_rows["date_loaded"])
            new_rows["is_current"] = True
            return ChangeSet(
                new_rows=new_rows.reset_index(drop=True),
                changed_rows=incoming.iloc[0:0].copy(),
                unchanged_rows=incoming.iloc[0:0].copy(),
            )

        existing_latest = existing.copy()
        if "date_loaded" in existing_latest.columns:
            existing_latest = existing_latest.sort_values(by="date_loaded", ascending=True, na_position="last")
        existing_latest = existing_latest.dropna(subset=[self.primary_key]).drop_duplicates(subset=[self.primary_key], keep="last")

        existing_hash_map = existing_latest.set_index(self.primary_key)[self.hash_column].to_dict()
        existing_created_map = existing_latest.set_index(self.primary_key)["date_created"].to_dict() if "date_created" in existing_latest.columns else {}

        new_rows = []
        changed_rows = []
        unchanged_rows = []

        for _, row in incoming.iterrows():
            key = row[self.primary_key]
            row_hash = row[self.hash_column]
            current_hash = existing_hash_map.get(key)

            if current_hash is None:
                new_row = row.copy()
                new_row["date_created"] = new_row["date_created"] if pd.notna(new_row["date_created"]) else new_row["date_loaded"]
                new_row["is_current"] = True
                new_rows.append(new_row)
                continue

            if current_hash == row_hash:
                unchanged_rows.append(row.copy())
                continue

            changed_row = row.copy()
            existing_created = existing_created_map.get(key)
            changed_row["date_created"] = existing_created if pd.notna(existing_created) else changed_row["date_loaded"]
            changed_row["is_current"] = True
            changed_rows.append(changed_row)

        def _rows_to_df(rows: list) -> DataFrame:
            if not rows:
                return incoming.iloc[0:0].copy()
            return DataFrame(rows).reset_index(drop=True)

        return ChangeSet(
            new_rows=_rows_to_df(new_rows),
            changed_rows=_rows_to_df(changed_rows),
            unchanged_rows=_rows_to_df(unchanged_rows),
        )
