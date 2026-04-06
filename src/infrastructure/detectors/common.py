from __future__ import annotations

import pandas as pd
from pandas import DataFrame

from src.domain.models.change_set import ChangeSet
from src.infrastructure.versioning.frame_utils import (
    latest_rows_by_primary_key,
    normalize_existing_versioned_frame,
    normalize_incoming_versioned_frame,
    prepare_changed_versioned_row,
    prepare_new_versioned_row,
)


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

        incoming = normalize_incoming_versioned_frame(candidates_df)

        if existing_df.empty:
            prepared_rows = incoming.apply(prepare_new_versioned_row, axis=1)
            return ChangeSet(
                new_rows=prepared_rows.reset_index(drop=True),
                changed_rows=incoming.iloc[0:0].copy(),
                unchanged_rows=incoming.iloc[0:0].copy(),
            )

        existing = normalize_existing_versioned_frame(existing_df)

        if self.primary_key not in existing.columns or self.hash_column not in existing.columns:
            prepared_rows = incoming.apply(prepare_new_versioned_row, axis=1)
            return ChangeSet(
                new_rows=prepared_rows.reset_index(drop=True),
                changed_rows=incoming.iloc[0:0].copy(),
                unchanged_rows=incoming.iloc[0:0].copy(),
            )

        existing_latest = latest_rows_by_primary_key(existing, self.primary_key)

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
                new_rows.append(prepare_new_versioned_row(row))
                continue

            if current_hash == row_hash:
                unchanged_rows.append(row.copy())
                continue

            existing_created = existing_created_map.get(key)
            changed_rows.append(prepare_changed_versioned_row(row, existing_created))

        def _rows_to_df(rows: list) -> DataFrame:
            if not rows:
                return incoming.iloc[0:0].copy()
            return DataFrame(rows).reset_index(drop=True)

        return ChangeSet(
            new_rows=_rows_to_df(new_rows),
            changed_rows=_rows_to_df(changed_rows),
            unchanged_rows=_rows_to_df(unchanged_rows),
        )
