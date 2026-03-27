from __future__ import annotations

from pandas import DataFrame
from sqlalchemy import text

from src.infrastructure.writing.sql_writer_base import BasePostgresSQLWriter
from src.infrastructure.writing.utils import quote_identifiers


class UpsertWriteStrategy(BasePostgresSQLWriter):
    def __init__(self, connector, table_name: str, primary_key: str):
        super().__init__(
            connector=connector,
            table_name=table_name,
            primary_key=primary_key,
        )

    def requires_primary_key(self) -> bool:
        return True

    def _initialize_target(self, engine, df: DataFrame) -> None:
        self._rename_temp_to_target(engine);

        with engine.begin() as conn:
            # Remove duplicates before creating the unique index
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

            index_name = self._build_unique_index_name(
                self.table_name,
                self.primary_key,
            )
            conn.execute(
                text(
                    f'CREATE UNIQUE INDEX IF NOT EXISTS "{index_name}" '
                    f'ON "{self.table_name}" ("{self.primary_key}")'
                )
            )

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

        index_name = self._build_unique_index_name(self.table_name, self.primary_key)

        with engine.begin() as conn:
            # Remove duplicates before creating the unique index
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

            conn.execute(
                text(
                    f'CREATE UNIQUE INDEX IF NOT EXISTS "{index_name}" '
                    f'ON "{self.table_name}" ("{self.primary_key}")'
                )
            )

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
