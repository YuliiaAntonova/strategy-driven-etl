from pandas import DataFrame
from sqlalchemy import text

from src.domain.contracts.write_strategy import BaseWriteStrategy
from src.infrastructure.writing.sql_writer_base import BasePostgresSQLWriter


class VersionedWriteStrategy(BaseWriteStrategy, BasePostgresSQLWriter):
    def __init__(self, connector, table_name: str, primary_key: str):
        BasePostgresSQLWriter.__init__(self, connector=connector, table_name=table_name)
        self.primary_key = primary_key

    def write(self, df: DataFrame, chunk_size: int | None = None) -> None:
        if df.empty:
            print("No rows to write")
            return
        if self.primary_key not in df.columns:
            raise ValueError(f"Primary key column '{self.primary_key}' not found in dataframe")
        engine, _ = self._stage_dataframe(df, chunk_size=chunk_size)
        if not self._target_exists(engine):
            with engine.begin() as conn:
                conn.execute(text(f'ALTER TABLE "{self.temp_table_name}" RENAME TO "{self.table_name}"'))
            print(f"Initialized '{self.table_name}' from staging '{self.temp_table_name}'")
            return
        quoted_columns = [f'"{column}"' for column in df.columns]
        select_columns = []
        for column in df.columns:
            if column == "date_created":
                select_columns.append('COALESCE(lt."date_created", s."date_created") AS "date_created"')
            else:
                select_columns.append(f's."{column}"')
        dedup_staging_cte = f'''
            WITH staged AS (
                SELECT *
                FROM (
                    SELECT
                        s.*,
                        ROW_NUMBER() OVER (
                            PARTITION BY s."{self.primary_key}"
                            ORDER BY s."date_loaded" DESC NULLS LAST
                        ) AS rn
                    FROM "{self.temp_table_name}" s
                ) ranked
                WHERE ranked.rn = 1
            ),
            latest_target AS (
                SELECT DISTINCT ON (t."{self.primary_key}")
                    t.*
                FROM "{self.table_name}" t
                WHERE t."is_current" = true
                ORDER BY t."{self.primary_key}", t."date_loaded" DESC NULLS LAST
            )
        '''
        update_sql = text(
            dedup_staging_cte + f'''
            UPDATE "{self.table_name}" t
            SET "is_current" = false
            FROM staged s
            WHERE t."{self.primary_key}" = s."{self.primary_key}"
              AND t."is_current" = true
              AND COALESCE(t."row_hash", '') <> COALESCE(s."row_hash", '')
            '''
        )
        insert_sql = text(
            dedup_staging_cte + f'''
            INSERT INTO "{self.table_name}" ({", ".join(quoted_columns)})
            SELECT {", ".join(select_columns)}
            FROM staged s
            LEFT JOIN latest_target lt
              ON lt."{self.primary_key}" = s."{self.primary_key}"
            WHERE lt."{self.primary_key}" IS NULL
               OR COALESCE(lt."row_hash", '') <> COALESCE(s."row_hash", '')
            '''
        )
        with engine.begin() as conn:
            updated_result = conn.execute(update_sql)
            inserted_result = conn.execute(insert_sql)
            conn.execute(text(f'DROP TABLE IF EXISTS "{self.temp_table_name}"'))
        print(f"Closed previous current versions for {updated_result.rowcount} rows")
        print(f"Inserted {inserted_result.rowcount} rows into '{self.table_name}' from staging '{self.temp_table_name}'")
