"""Change detector for incremental loads based on a row hash column."""

from __future__ import annotations

from pandas import DataFrame

from src.domain.contracts.change_detector import BaseChangeDetector
from src.domain.models.change_set import ChangeSet
from src.infrastructure.detectors.common import BaseTabularChangeDetector


def _filter_unseen_hashes(
    incoming_df: DataFrame,
    existing_df: DataFrame,
    *,
    hash_column: str,
) -> DataFrame:
    if incoming_df.empty or existing_df.empty:
        return incoming_df

    existing_hashes = set(existing_df[hash_column].dropna().astype(str))
    incoming = incoming_df.copy()
    return incoming[~incoming[hash_column].astype(str).isin(existing_hashes)]


class IncrementalByHashDetector(BaseTabularChangeDetector, BaseChangeDetector):
    """Detect new rows by comparing incoming hashes against existing hashes."""

    def __init__(self, primary_key: str, hash_column: str = "row_hash"):
        super().__init__(primary_key=primary_key, hash_column=hash_column)

    def detect(self, incoming_df: DataFrame, existing_df: DataFrame) -> ChangeSet:
        candidates = _filter_unseen_hashes(
            incoming_df,
            existing_df,
            hash_column=self.hash_column,
        )
        return self._classify_candidates(candidates, existing_df)
