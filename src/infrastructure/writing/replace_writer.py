from __future__ import annotations

from pandas import DataFrame
from sqlalchemy import text

from src.infrastructure.writing.sql_writer_base import BasePostgresSQLWriter


class ReplaceWriteStrategy(BasePostgresSQLWriter):
    def _initialize_target(self, engine, df: DataFrame) -> None:
        self._rename_temp_to_target(engine)

        with engine.begin() as conn:
            # Remove duplicates before renaming the table
            conn.execute(
                text(
                    f'''
                    DELETE FROM "{self.table_name}"
                    WHERE ctid NOT IN (
                        SELECT MIN(ctid)
                        FROM "{self.table_name}"
                        GROUP BY "{self.primary_key}"
                    )
                    '''
                )
            )

        print(f"Initialized '{self.table_name}' with {len(df)} rows")

    def _write_to_existing_target(self, engine, df: DataFrame) -> None:
        with engine.begin() as conn:
            conn.execute(text(f'DROP TABLE IF EXISTS "{self.table_name}"'))
            conn.execute(
                text(
                    f'ALTER TABLE "{self.temp_table_name}" '
                    f'RENAME TO "{self.table_name}"'
                )
            )
        print(f"Replaced '{self.table_name}' with {len(df)} rows")
