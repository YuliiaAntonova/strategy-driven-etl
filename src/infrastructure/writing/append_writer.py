from __future__ import annotations

from pandas import DataFrame
from sqlalchemy import text

from src.infrastructure.writing.sql_writer_base import BasePostgresSQLWriter


class AppendWriteStrategy(BasePostgresSQLWriter):
    def _write_to_existing_target(self, engine, df: DataFrame) -> None:
        columns = [f'"{column}"' for column in df.columns]
        columns_sql = ", ".join(columns)

        sql = text(
            f'''
            INSERT INTO "{self.table_name}" ({columns_sql})
            SELECT {columns_sql}
            FROM "{self.temp_table_name}"
            '''
        )

        with engine.begin() as conn:
            result = conn.execute(sql)

        print(f"Appended {result.rowcount} rows into '{self.table_name}'")
