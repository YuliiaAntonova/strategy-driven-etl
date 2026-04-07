"""Postgres loader for historized/versioned writes.

This is a loader (not a writer) because it performs a domain-specific
"versioned" merge into a target table using a staging temp table.
"""

from pandas import DataFrame
from sqlalchemy import inspect, text

from src.domain.contracts.loader import BaseLoader
from src.infrastructure.connectors.postgres import PostgreSQLConnector
from src.infrastructure.utils.postgres_staging import build_dtype_map
from src.infrastructure.writing.sql_writer_base import BasePostgresSQLWriter
from src.infrastructure.writing.utils import (
    build_versioned_dedup_cte,
    quote_identifiers,
)


class VersionedPostgresLoader(BaseLoader):
    """Load a dataframe into a Postgres table using historized semantics."""

    def __init__(
        self,
        connector: PostgreSQLConnector,
        table_name: str,
        primary_key: str,
    ):
        self.connector = connector
        self.table_name = table_name
        self.primary_key = primary_key
        self.temp_table_name = f"{table_name}_temp"

    def _dtype_map(self, df: DataFrame) -> dict:
        return build_dtype_map(df)

    def load(self, df: DataFrame, chunk_size: int | None = None) -> None:
        if df.empty:
            print("No rows to load")
            return

        if self.primary_key not in df.columns:
            raise ValueError(f"Primary key column '{self.primary_key}' not found in dataframe")

        engine = self.connector.connect()
        dtype_map = self._dtype_map(df)
        BasePostgresSQLWriter.stage_dataframe_to_table(
            engine=engine,
            df=df,
            temp_table_name=self.temp_table_name,
            chunk_size=chunk_size,
        )

        inspector = inspect(engine)
        target_exists = inspector.has_table(self.table_name)

        if not target_exists:
            df.to_sql(
                name=self.table_name,
                con=engine,
                if_exists="replace",
                index=False,
                dtype=dtype_map,
            )
            with engine.begin() as conn:
                conn.execute(text(f'DROP TABLE IF EXISTS "{self.temp_table_name}"'))
            print(f"Initialized '{self.table_name}' from staging table '{self.temp_table_name}'")
            print(f"Loaded {len(df)} versioned rows into table '{self.table_name}'")
            return

        quoted_columns = quote_identifiers(df.columns)
        select_columns = []
        for column in df.columns:
            if column == "date_created":
                select_columns.append('COALESCE(lt."date_created", s."date_created") AS "date_created"')
            else:
                select_columns.append(f's."{column}"')

        dedup_staging_cte = build_versioned_dedup_cte(
            temp_table_name=self.temp_table_name,
            target_table_name=self.table_name,
            primary_key=self.primary_key,
            only_current=False,
        )

        update_sql = text(
            dedup_staging_cte
            + f"""
            UPDATE "{self.table_name}" t
            SET "is_current" = false
            FROM staged s
            WHERE t."{self.primary_key}" = s."{self.primary_key}"
              AND t."is_current" = true
              AND COALESCE(t."row_hash", '') <> COALESCE(s."row_hash", '')
            """
        )

        insert_sql = text(
            dedup_staging_cte
            + f"""
            INSERT INTO "{self.table_name}" ({", ".join(quoted_columns)})
            SELECT {", ".join(select_columns)}
            FROM staged s
            LEFT JOIN latest_target lt
              ON lt."{self.primary_key}" = s."{self.primary_key}"
            WHERE lt."{self.primary_key}" IS NULL
               OR COALESCE(lt."row_hash", '') <> COALESCE(s."row_hash", '')
            """
        )

        with engine.begin() as conn:
            updated_result = conn.execute(update_sql)
            inserted_result = conn.execute(insert_sql)
            conn.execute(text(f'DROP TABLE IF EXISTS "{self.temp_table_name}"'))

        print(f"Closed previous current versions for {updated_result.rowcount} rows")
        print(
            f"Inserted {inserted_result.rowcount} rows into table '{self.table_name}' "
            f"from staging '{self.temp_table_name}'"
        )
