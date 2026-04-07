"""Upsert write strategy for Postgres targets."""

from __future__ import annotations

from pandas import DataFrame
from sqlalchemy import text

from src.infrastructure.writing.sql_writer_base import PrimaryKeyPostgresSQLWriter
from src.infrastructure.writing.utils import quote_identifiers


class UpsertWriteStrategy(PrimaryKeyPostgresSQLWriter):
    """Upserts staged rows into the target table using ON CONFLICT."""

    def _prepare_target_for_upsert(self, conn) -> None:
        self._delete_duplicate_rows(conn, self.table_name)
        self._ensure_unique_index(conn, self.table_name)

    def _initialize_target(self, engine, df: DataFrame) -> None:
        self._rename_temp_to_target(engine)

        with engine.begin() as conn:
            self._prepare_target_for_upsert(conn)

        print(
            f"Initialized '{self.table_name}' with {len(df)} rows "
            f"and unique index on '{self.primary_key}'"
        )

    def _write_to_existing_target(self, engine, df: DataFrame) -> None:
        columns = list(df.columns)
        quoted_columns = quote_identifiers(columns)
        insert_columns_sql = ", ".join(quoted_columns)
        select_columns_sql = ", ".join(quoted_columns)

        update_columns = [column for column in columns if column != self.primary_key]
        update_assignments = ", ".join(
            f'"{column}" = EXCLUDED."{column}"' for column in update_columns
        )

        with engine.begin() as conn:
            self._prepare_target_for_upsert(conn)

            sql = text(
                f'''
                INSERT INTO "{self.table_name}" ({insert_columns_sql})
                SELECT {select_columns_sql}
                FROM "{self.temp_table_name}"
                ON CONFLICT ("{self.primary_key}") DO UPDATE SET {update_assignments}
                '''
            )

            result = conn.execute(sql)

        print(f"Upserted {result.rowcount} rows into '{self.table_name}'")
