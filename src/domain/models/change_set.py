from __future__ import annotations

from dataclasses import dataclass

import pandas as pd
from pandas import DataFrame


@dataclass(frozen=True)
class ChangeSet:
    new_rows: DataFrame
    changed_rows: DataFrame
    unchanged_rows: DataFrame

    @classmethod
    def empty_like(cls, sample_df: DataFrame) -> "ChangeSet":
        empty = sample_df.iloc[0:0].copy()
        return cls(new_rows=empty.copy(), changed_rows=empty.copy(), unchanged_rows=empty.copy())

    @property
    def rows_to_write(self) -> DataFrame:
        frames = [frame for frame in (self.new_rows, self.changed_rows) if not frame.empty]
        if not frames:
            return self.new_rows.iloc[0:0].copy() if not self.new_rows.empty else self.changed_rows.iloc[0:0].copy()
        return pd.concat(frames, ignore_index=True)

    @property
    def has_writes(self) -> bool:
        return not self.rows_to_write.empty
