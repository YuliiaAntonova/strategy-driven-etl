"""Change detector using primary key + row hash.

Classifies incoming rows into new/changed/unchanged by comparing the latest
existing hash per primary key.
"""

from __future__ import annotations

from pandas import DataFrame

from src.domain.contracts.change_detector import BaseChangeDetector
from src.domain.models.change_set import ChangeSet
from src.infrastructure.detectors.common import BaseTabularChangeDetector
from src.infrastructure.detectors.frame_utils import (
    latest_rows_by_primary_key,
    normalize_existing_versioned_frame,
    normalize_incoming_versioned_frame,
    prepare_changed_versioned_row,
    prepare_new_versioned_row,
)


def _prepare_pk_hash_candidates(
    incoming_df: DataFrame,
    existing_df: DataFrame,
    *,
    primary_key: str,
    hash_column: str,
) -> DataFrame:
    if incoming_df.empty:
        return incoming_df

    if primary_key not in incoming_df.columns:
        raise ValueError(f"Primary key column '{primary_key}' not found in incoming data")
    if hash_column not in incoming_df.columns:
        raise ValueError(f"Hash column '{hash_column}' not found in incoming data")

    incoming = normalize_incoming_versioned_frame(incoming_df)

    if existing_df.empty:
        return incoming.apply(prepare_new_versioned_row, axis=1)

    if primary_key not in existing_df.columns:
        raise ValueError(f"Primary key column '{primary_key}' not found in existing data")
    if hash_column not in existing_df.columns:
        raise ValueError(
            f"Hash column '{hash_column}' not found in existing data. Run full load first."
        )

    existing = normalize_existing_versioned_frame(existing_df)
    existing_latest = latest_rows_by_primary_key(existing, primary_key)

    existing_hash_map = existing_latest.set_index(primary_key)[hash_column].to_dict()
    existing_created_map = existing_latest.set_index(primary_key)["date_created"].to_dict()

    rows = []
    for _, row in incoming.iterrows():
        key = row[primary_key]
        row_hash = row[hash_column]

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


class IncrementalByPrimaryKeyAndHashDetector(BaseTabularChangeDetector, BaseChangeDetector):
    """Detect changes by comparing PK + row hash against the latest snapshot."""

    def __init__(self, primary_key: str, hash_column: str = "row_hash"):
        super().__init__(primary_key=primary_key, hash_column=hash_column)

    def detect(self, incoming_df: DataFrame, existing_df: DataFrame) -> ChangeSet:
        assert self.primary_key is not None
        candidates = _prepare_pk_hash_candidates(
            incoming_df,
            existing_df,
            primary_key=self.primary_key,
            hash_column=self.hash_column,
        )
        return self._classify_candidates(candidates, existing_df)
