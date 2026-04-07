"""Versioned (historized) write strategy for Postgres targets.

Maintains a full history of changes by inserting new versions and marking
previous versions as not current.
"""

from __future__ import annotations

from pandas import DataFrame
from sqlalchemy import text

from src.infrastructure.writing.sql_writer_base import PrimaryKeyPostgresSQLWriter
from src.infrastructure.writing.utils import quote_identifiers


class VersionedWriteStrategy(PrimaryKeyPostgresSQLWriter):
    """Writes historized rows (SCD2-like) into the target table."""

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

    def _versioned_source_cte(self) -> str:
        return f'''
            WITH staged AS (
                SELECT *
                FROM (
                    SELECT
                        staged_source.*,
                        ROW_NUMBER() OVER (
                            PARTITION BY staged_source."{self.primary_key}"
                            ORDER BY staged_source."date_loaded" DESC NULLS LAST
                        ) AS row_number_rank
                    FROM "{self.temp_table_name}" staged_source
                ) ranked_stage
                WHERE ranked_stage.row_number_rank = 1
            ),
            current_target AS (
                SELECT DISTINCT ON (target."{self.primary_key}")
                    target.*
                FROM "{self.table_name}" target
                WHERE target."is_current" = true
                ORDER BY target."{self.primary_key}", target."date_loaded" DESC NULLS LAST
            )
        '''

    def _write_to_existing_target(self, engine, df: DataFrame) -> None:
        insert_columns_sql = ", ".join(quote_identifiers(df.columns))
        staged_columns_sql = ", ".join(
            f'staged."{column}"' for column in df.columns
        )
        versioned_source_cte = self._versioned_source_cte()

        with engine.begin() as conn:
            conn.execute(
                text(
                    f'''
                    {versioned_source_cte}
                    UPDATE "{self.table_name}" AS target
                    SET "is_current" = false
                    FROM staged
                    JOIN current_target
                      ON current_target."{self.primary_key}" = staged."{self.primary_key}"
                    WHERE target."{self.primary_key}" = current_target."{self.primary_key}"
                      AND target."row_hash" = current_target."row_hash"
                      AND target."is_current" = true
                      AND staged."row_hash" <> current_target."row_hash"
                    '''
                )
            )

            result = conn.execute(
                text(
                    f'''
                    {versioned_source_cte}
                    INSERT INTO "{self.table_name}" ({insert_columns_sql})
                    SELECT {staged_columns_sql}
                    FROM staged
                    LEFT JOIN current_target
                      ON current_target."{self.primary_key}" = staged."{self.primary_key}"
                    WHERE current_target."{self.primary_key}" IS NULL
                       OR staged."row_hash" <> current_target."row_hash"
                    '''
                )
            )

        print(f"Versioned {result.rowcount} rows into '{self.table_name}'")
