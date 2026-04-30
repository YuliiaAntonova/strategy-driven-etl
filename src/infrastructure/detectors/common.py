"""Shared helpers for tabular change detectors.

`BaseTabularChangeDetector` contains shared logic for classifying incoming rows
into new/changed/unchanged buckets for incremental/versioned workflows.
"""

from __future__ import annotations

from pandas import DataFrame

from src.domain.models.change_set import ChangeSet
from src.infrastructure.detectors.frame_utils import (
    latest_rows_by_primary_key,
    normalize_existing_versioned_frame,
    normalize_incoming_versioned_frame,
    prepare_changed_versioned_row,
    prepare_new_versioned_row,
)


class BaseTabularChangeDetector:
    """Common implementation for detectors operating on pandas DataFrames."""

    def __init__(self, primary_key: str | None = None, hash_column: str = "row_hash"):
        self.primary_key = primary_key
        self.hash_column = hash_column

    def _empty_like_incoming(self, incoming_df: DataFrame) -> DataFrame:
        return incoming_df.iloc[0:0].copy()

    def _rows_to_df(self, rows: list, incoming_template: DataFrame) -> DataFrame:
        if not rows:
            return self._empty_like_incoming(incoming_template)
        return DataFrame(rows).reset_index(drop=True)

    def _validate_required_columns(self, df: DataFrame) -> None:
        if not self.primary_key:
            return
        if self.primary_key not in df.columns:
            raise ValueError(
                f"Primary key column '{self.primary_key}' not found in incoming data"
            )
        if self.hash_column not in df.columns:
            raise ValueError(
                f"Hash column '{self.hash_column}' not found in incoming data"
            )

    def _new_only_changeset(self, incoming: DataFrame) -> ChangeSet:
        prepared_rows = incoming.apply(prepare_new_versioned_row, axis=1)
        empty = self._empty_like_incoming(incoming)
        return ChangeSet(
            new_rows=prepared_rows.reset_index(drop=True),
            changed_rows=empty.copy(),
            unchanged_rows=empty.copy(),
        )

    def _existing_maps(self, existing_df: DataFrame) -> tuple[dict, dict]:
        existing_latest = latest_rows_by_primary_key(existing_df, self.primary_key)
        hash_map = (
            existing_latest.set_index(self.primary_key)[self.hash_column].to_dict()
        )
        created_map = (
            existing_latest.set_index(self.primary_key)["date_created"].to_dict()
            if "date_created" in existing_latest.columns
            else {}
        )
        return hash_map, created_map

    def _split_by_hash_change(
        self,
        *,
        incoming: DataFrame,
        existing_hash_map: dict,
        existing_created_map: dict,
    ) -> tuple[list, list, list]:
        new_rows: list = []
        changed_rows: list = []
        unchanged_rows: list = []

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

        return new_rows, changed_rows, unchanged_rows

    def _classify_candidates(
        self,
        candidates_df: DataFrame,
        existing_df: DataFrame,
    ) -> ChangeSet:
        if candidates_df.empty:
            return ChangeSet.empty_like(candidates_df)

        if not self.primary_key:
            empty = self._empty_like_incoming(candidates_df)
            return ChangeSet(
                new_rows=candidates_df.reset_index(drop=True),
                changed_rows=empty.copy(),
                unchanged_rows=empty.copy(),
            )

        self._validate_required_columns(candidates_df)

        incoming = normalize_incoming_versioned_frame(candidates_df)

        if existing_df.empty:
            return self._new_only_changeset(incoming)

        existing = normalize_existing_versioned_frame(existing_df)

        if (
            self.primary_key not in existing.columns
            or self.hash_column not in existing.columns
        ):
            return self._new_only_changeset(incoming)

        existing_hash_map, existing_created_map = self._existing_maps(existing)

        new_rows, changed_rows, unchanged_rows = self._split_by_hash_change(
            incoming=incoming,
            existing_hash_map=existing_hash_map,
            existing_created_map=existing_created_map,
        )

        return ChangeSet(
            new_rows=self._rows_to_df(new_rows, incoming),
            changed_rows=self._rows_to_df(changed_rows, incoming),
            unchanged_rows=self._rows_to_df(unchanged_rows, incoming),
        )
