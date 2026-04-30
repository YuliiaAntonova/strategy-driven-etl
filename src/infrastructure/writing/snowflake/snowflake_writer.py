from __future__ import annotations

from pandas import DataFrame
from sqlalchemy import text

from src.infrastructure.writing.shared.staged_sql_writer import StagedSqlTableWriter
from src.infrastructure.writing.shared.utils import quote_identifiers


class SnowflakeBaseWriteStrategy(StagedSqlTableWriter):
    """Snowflake-specific merge SQL; staging lifecycle lives in StagedSqlTableWriter."""


class SnowflakeReplaceWriteStrategy(SnowflakeBaseWriteStrategy):
    def _write_to_existing_target(self, engine, df: DataFrame) -> None:
        with engine.begin() as conn:
            conn.execute(text(f'DROP TABLE IF EXISTS "{self.table_name}"'))
            conn.execute(
                text(
                    f'ALTER TABLE "{self.temp_table_name}" '
                    f'RENAME TO "{self.table_name}"'
                )
            )

        print(f"Replaced Snowflake table '{self.table_name}' with {len(df)} rows")


class SnowflakeAppendWriteStrategy(SnowflakeBaseWriteStrategy):
    def _write_to_existing_target(self, engine, df: DataFrame) -> None:
        columns_sql = ", ".join(quote_identifiers(df.columns))

        with engine.begin() as conn:
            result = conn.execute(
                text(
                    f'''
                    INSERT INTO "{self.table_name}" ({columns_sql})
                    SELECT {columns_sql}
                    FROM "{self.temp_table_name}"
                    '''
                )
            )

        print(f"Appended {result.rowcount} rows into Snowflake table '{self.table_name}'")


class SnowflakeVersionedWriteStrategy(SnowflakeBaseWriteStrategy):
    def requires_primary_key(self) -> bool:
        return True

    def _validate_input(self, df: DataFrame) -> None:
        super()._validate_input(df)

        required_columns = {"row_hash", "date_created", "date_loaded", "is_current"}
        missing_columns = sorted(required_columns - set(df.columns))

        if missing_columns:
            raise ValueError(
                "Snowflake versioned write mode requires columns: "
                f"{sorted(required_columns)}. Missing: {missing_columns}"
            )

    def _write_to_existing_target(self, engine, df: DataFrame) -> None:
        insert_columns_sql = ", ".join(quote_identifiers(df.columns))
        staged_columns_sql = ", ".join(f'staged."{column}"' for column in df.columns)

        staged_cte = f'''
            WITH staged AS (
                SELECT *
                FROM "{self.temp_table_name}"
                QUALIFY ROW_NUMBER() OVER (
                    PARTITION BY "{self.primary_key}"
                    ORDER BY "date_loaded" DESC NULLS LAST
                ) = 1
            ),
            current_target AS (
                SELECT *
                FROM "{self.table_name}"
                WHERE "is_current" = TRUE
                QUALIFY ROW_NUMBER() OVER (
                    PARTITION BY "{self.primary_key}"
                    ORDER BY "date_loaded" DESC NULLS LAST
                ) = 1
            )
        '''

        with engine.begin() as conn:
            conn.execute(
                text(
                    f'''
                    {staged_cte}
                    UPDATE "{self.table_name}" AS target
                    SET "is_current" = FALSE
                    FROM staged
                    JOIN current_target
                      ON current_target."{self.primary_key}" = staged."{self.primary_key}"
                    WHERE target."{self.primary_key}" = current_target."{self.primary_key}"
                      AND target."row_hash" = current_target."row_hash"
                      AND target."is_current" = TRUE
                      AND staged."row_hash" <> current_target."row_hash"
                    '''
                )
            )

            result = conn.execute(
                text(
                    f'''
                    {staged_cte}
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

        print(f"Versioned {result.rowcount} rows into Snowflake table '{self.table_name}'")
