from __future__ import annotations

from pandas import DataFrame
from sqlalchemy import text

from src.infrastructure.writing.sql_writer_base import BasePostgresSQLWriter


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
        quoted_columns = [f'"{column}"' for column in df.columns]
        insert_columns_sql = ", ".join(quoted_columns)

        select_columns_sql_parts = []
        for column in df.columns:
            if column == "date_created":
                select_columns_sql_parts.append(
                    'COALESCE(latest_target."date_created", staged."date_created") '
                    'AS "date_created"'
                )
            else:
                select_columns_sql_parts.append(f'staged."{column}"')

        select_columns_sql = ", ".join(select_columns_sql_parts)

        dedup_staging_cte = f'''
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
            latest_target AS (
                SELECT DISTINCT ON (target."{self.primary_key}")
                    target.*
                FROM "{self.table_name}" target
                WHERE target."is_current" = true
                ORDER BY target."{self.primary_key}", target."date_loaded" DESC NULLS LAST
            )
        '''

        close_previous_versions_sql = text(
            dedup_staging_cte
            + f'''
            UPDATE "{self.table_name}" target
            SET "is_current" = false
            FROM staged
            WHERE target."{self.primary_key}" = staged."{self.primary_key}"
              AND target."is_current" = true
              AND COALESCE(target."row_hash", '') <> COALESCE(staged."row_hash", '')
            '''
        )

        insert_new_versions_sql = text(
            dedup_staging_cte
            + f'''
            INSERT INTO "{self.table_name}" ({insert_columns_sql})
            SELECT {select_columns_sql}
            FROM staged
            LEFT JOIN latest_target
              ON latest_target."{self.primary_key}" = staged."{self.primary_key}"
            WHERE latest_target."{self.primary_key}" IS NULL
               OR COALESCE(latest_target."row_hash", '')
                  <> COALESCE(staged."row_hash", '')
            '''
        )

        with engine.begin() as conn:
            updated_result = conn.execute(close_previous_versions_sql)
            inserted_result = conn.execute(insert_new_versions_sql)

        print(
            f"Closed previous current versions for {updated_result.rowcount} rows"
        )
        print(
            f"Inserted {inserted_result.rowcount} new/changed versioned rows "
            f"into '{self.table_name}'"
        )
