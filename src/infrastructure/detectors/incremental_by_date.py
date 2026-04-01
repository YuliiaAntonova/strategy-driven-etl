from __future__ import annotations

from pandas import DataFrame

from src.domain.contracts.change_detector import BaseChangeDetector
from src.domain.models.change_set import ChangeSet
from src.infrastructure.detectors.common import BaseTabularChangeDetector
from src.infrastructure.versioning.incremental_by_date import IncrementalByDateStrategy


class IncrementalByDateDetector(BaseTabularChangeDetector, BaseChangeDetector):
    def __init__(self, date_column: str, primary_key: str, hash_column: str = "row_hash"):
        super().__init__(primary_key=primary_key, hash_column=hash_column)
        self.strategy = IncrementalByDateStrategy(date_column=date_column)

    def detect(self, incoming_df: DataFrame, existing_df: DataFrame) -> ChangeSet:
        candidates = self.strategy.prepare(incoming_df=incoming_df, existing_df=existing_df)
        return self._classify_candidates(candidates, existing_df)
