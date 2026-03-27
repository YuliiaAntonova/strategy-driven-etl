from __future__ import annotations

from pandas import DataFrame
from sqlalchemy import text

from src.infrastructure.writing.sql_writer_base import BasePostgresSQLWriter
from src.infrastructure.writing.utils import (
    quote_identifiers,
    build_versioned_dedup_cte,
)


class VersionedWriteStrategy(BasePostgresSQLWriter):
    def __init__(self, connector, table_name: str, primary_key: str):
        super().__init__(
            connector=connector,
            table_name=table_name,
            primary_key=primary_key,
        )

    def requires_primary_key(self) -> bool:
        return True

    def _validate_input(self, df: DataFrame) -> None:
        super()._validate_input(df)
        required_columns = {"row_hash", "date_created", "date_loaded", "is_current"}
        missing_columns = sorted(required_columns - set(df.columns))
        if missing_columns:
            raise ValueError(
                "Versioned write mode requires columns: "
                f"{sorted(required_columns)}. Missing: {missing_columns}"
            )

    def _initialize_target(self, engine, df: DataFrame) -> None:
        self._rename_temp_to_target(engine)

        with engine.begin() as conn:
            primary_key_index_name = self._build_index_name(
                self.table_name,
                [self.primary_key],
            )
            conn.execute(
                text(
                    f'CREATE INDEX IF NOT EXISTS "{primary_key_index_name}" '
                    f'ON "{self.table_name}" ("{self.primary_key}")'
                )
            )

            primary_key_hash_index_name = self._build_index_name(
                self.table_name,
                [self.primary_key, "row_hash"],
            )
            conn.execute(
                text(
                    f'CREATE INDEX IF NOT EXISTS "{primary_key_hash_index_name}" '
                    f'ON "{self.table_name}" ("{self.primary_key}", "row_hash")'
                )
            )

        print(f"Initialized versioned table '{self.table_name}' with {len(df)} rows")

    def _write_to_existing_target(self, engine, df: DataFrame) -> None:
        columns_sql = ", ".join(quote_identifiers(df.columns))

        with engine.begin() as conn:
            # Remove duplicates before inserting new versions
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

            dedup_cte = build_versioned_dedup_cte(self.table_name, self.primary_key)
            sql = text(
                f'''
                WITH dedup AS ({dedup_cte})
                INSERT INTO "{self.table_name}" ({columns_sql})
                SELECT {columns_sql}
                FROM dedup
                '''
            )

            result = conn.execute(sql)

        print(f"Versioned {result.rowcount} rows into '{self.table_name}'")
