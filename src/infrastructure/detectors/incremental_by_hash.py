"""Change detector for incremental loads based on a row hash column."""

from __future__ import annotations

from pandas import DataFrame

from src.domain.contracts.change_detector import BaseChangeDetector
from src.domain.models.change_set import ChangeSet
from src.infrastructure.detectors.common import BaseTabularChangeDetector
from src.infrastructure.versioning.incremental_by_hash import (
    IncrementalByHashStrategy,
)


class IncrementalByHashDetector(BaseTabularChangeDetector, BaseChangeDetector):
    """Detect new rows by comparing incoming hashes against existing hashes."""

    def __init__(self, primary_key: str, hash_column: str = "row_hash"):
        super().__init__(primary_key=primary_key, hash_column=hash_column)
        self.strategy = IncrementalByHashStrategy(hash_column=hash_column)

    def detect(self, incoming_df: DataFrame, existing_df: DataFrame) -> ChangeSet:
        candidates = self.strategy.prepare(
            incoming_df=incoming_df,
            existing_df=existing_df,
        )
        return self._classify_candidates(candidates, existing_df)
