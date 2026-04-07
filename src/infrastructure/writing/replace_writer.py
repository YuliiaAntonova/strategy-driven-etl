"""Replace write strategy for Postgres targets."""

from __future__ import annotations

from pandas import DataFrame
from src.infrastructure.writing.sql_writer_base import BasePostgresSQLWriter


class ReplaceWriteStrategy(BasePostgresSQLWriter):
    """Replaces the target table with the staged table contents."""

    def _initialize_target(self, engine, df: DataFrame) -> None:
        self._rename_temp_to_target(engine)

        with engine.begin() as conn:
            self._delete_duplicate_rows(conn, self.table_name)

        print(f"Initialized '{self.table_name}' with {len(df)} rows")

    def _write_to_existing_target(self, engine, df: DataFrame) -> None:
        with engine.begin() as conn:
            self._replace_target_with_staged(conn)
            self._delete_duplicate_rows(conn, self.table_name)

        print(f"Replaced '{self.table_name}' with {len(df)} rows")
