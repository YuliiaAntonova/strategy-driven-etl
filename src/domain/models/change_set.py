"""Domain model representing detected changes between incoming and existing data."""

from __future__ import annotations

from dataclasses import dataclass

import pandas as pd
from pandas import DataFrame


@dataclass(frozen=True)
class ChangeSet:
    """Holds rows partitioned into new/changed/unchanged buckets."""

    new_rows: DataFrame
    changed_rows: DataFrame
    unchanged_rows: DataFrame

    @classmethod
    def empty_like(cls, sample_df: DataFrame) -> "ChangeSet":
        """Create an empty ChangeSet with the same schema as sample_df."""
        empty = sample_df.iloc[0:0].copy()
        return cls(
            new_rows=empty.copy(),
            changed_rows=empty.copy(),
            unchanged_rows=empty.copy(),
        )

    @property
    def rows_to_write(self) -> DataFrame:
        """Return a dataframe containing rows that should be written.

        We write only new + changed rows. If there are no rows to write, return
        an empty dataframe with a stable schema.
        """

        frames = [df for df in (self.new_rows, self.changed_rows) if not df.empty]
        if frames:
            return pd.concat(frames, ignore_index=True)

        if not self.new_rows.empty:
            return self.new_rows.iloc[0:0].copy()
        return self.changed_rows.iloc[0:0].copy()

    @property
    def has_writes(self) -> bool:
        """True if there are any rows that will be written."""
        return not self.rows_to_write.empty
