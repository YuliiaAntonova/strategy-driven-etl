"""Change detector for incremental loads based on a primary key."""

from __future__ import annotations

from pandas import DataFrame

from src.domain.contracts.change_detector import BaseChangeDetector
from src.domain.models.change_set import ChangeSet
from src.infrastructure.detectors.common import BaseTabularChangeDetector


def _filter_new_primary_keys(
    incoming_df: DataFrame,
    existing_df: DataFrame,
    *,
    primary_key: str,
) -> DataFrame:
    if incoming_df.empty or existing_df.empty:
        return incoming_df

    existing_keys = set(existing_df[primary_key].dropna().astype(str))
    incoming = incoming_df.copy()
    return incoming[~incoming[primary_key].astype(str).isin(existing_keys)]


class IncrementalByPrimaryKeyDetector(BaseTabularChangeDetector, BaseChangeDetector):
    """Detect new rows where the primary key is not present in existing data."""

    def __init__(self, primary_key: str, hash_column: str = "row_hash"):
        super().__init__(primary_key=primary_key, hash_column=hash_column)

    def detect(self, incoming_df: DataFrame, existing_df: DataFrame) -> ChangeSet:
        assert self.primary_key is not None
        candidates = _filter_new_primary_keys(
            incoming_df,
            existing_df,
            primary_key=self.primary_key,
        )
        return self._classify_candidates(candidates, existing_df)
