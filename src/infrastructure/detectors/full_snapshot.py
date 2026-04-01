from __future__ import annotations

from pandas import DataFrame

from src.domain.contracts.change_detector import BaseChangeDetector
from src.domain.models.change_set import ChangeSet
from src.infrastructure.detectors.common import BaseTabularChangeDetector


class FullSnapshotDetector(BaseTabularChangeDetector, BaseChangeDetector):
    def detect(self, incoming_df: DataFrame, existing_df: DataFrame) -> ChangeSet:
        if incoming_df.empty:
            return ChangeSet.empty_like(incoming_df)
        empty = incoming_df.iloc[0:0].copy()
        return ChangeSet(
            new_rows=incoming_df.reset_index(drop=True),
            changed_rows=empty.copy(),
            unchanged_rows=empty.copy(),
        )
