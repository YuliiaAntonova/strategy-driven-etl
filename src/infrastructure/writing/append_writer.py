from __future__ import annotations

from pandas import DataFrame
from sqlalchemy import text

from src.infrastructure.writing.sql_writer_base import BasePostgresSQLWriter
from src.infrastructure.writing.utils import quote_identifiers


class AppendWriteStrategy(BasePostgresSQLWriter):
    def _write_to_existing_target(self, engine, df: DataFrame) -> None:
        columns_sql = ", ".join(quote_identifiers(df.columns))

        with engine.begin() as conn:
            # Remove duplicates before appending new data
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

            sql = text(
                f'''
                INSERT INTO "{self.table_name}" ({columns_sql})
                SELECT {columns_sql}
                FROM "{self.temp_table_name}"
                '''
            )

            result = conn.execute(sql)

        print(f"Appended {result.rowcount} rows into '{self.table_name}'")
