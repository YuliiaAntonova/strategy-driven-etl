"""Change detector for incremental loads based on a date/datetime column."""

from __future__ import annotations

import pandas as pd
from pandas import DataFrame

from src.domain.contracts.change_detector import BaseChangeDetector
from src.domain.models.change_set import ChangeSet
from src.infrastructure.detectors.common import BaseTabularChangeDetector


def _filter_newer_than_latest_date(
    incoming_df: DataFrame,
    existing_df: DataFrame,
    *,
    date_column: str,
) -> DataFrame:
    if incoming_df.empty or existing_df.empty:
        return incoming_df

    incoming = incoming_df.copy()
    existing = existing_df.copy()

    incoming[date_column] = pd.to_datetime(incoming[date_column], errors="coerce")
    existing[date_column] = pd.to_datetime(existing[date_column], errors="coerce")

    max_existing_date = existing[date_column].max()
    if pd.isna(max_existing_date):
        return incoming

    return incoming[incoming[date_column] > max_existing_date]


class IncrementalByDateDetector(BaseTabularChangeDetector, BaseChangeDetector):
    """Detect new rows by comparing a date column to the latest existing date."""

    def __init__(
        self,
        date_column: str,
        primary_key: str,
        hash_column: str = "row_hash",
    ):
        super().__init__(primary_key=primary_key, hash_column=hash_column)
        self.date_column = date_column

    def detect(self, incoming_df: DataFrame, existing_df: DataFrame) -> ChangeSet:
        candidates = _filter_newer_than_latest_date(
            incoming_df,
            existing_df,
            date_column=self.date_column,
        )
        return self._classify_candidates(candidates, existing_df)
