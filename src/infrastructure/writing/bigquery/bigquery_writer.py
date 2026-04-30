"""BigQuery write strategies: replace / append via ``to_sql``, merge via staging + ``MERGE``."""

from __future__ import annotations

import uuid
from abc import abstractmethod

from pandas import DataFrame
from sqlalchemy import text

from src.domain.contracts.write_strategy import BaseWriteStrategy
from src.domain.models.change_set import ChangeSet


def _as_dataframe(payload: DataFrame | ChangeSet) -> DataFrame:
    if isinstance(payload, ChangeSet):
        return payload.rows_to_write
    return payload


class BigQueryBaseWriteStrategy(BaseWriteStrategy):
    def __init__(self, connector, table_name: str, primary_key: str | None = None):
        self.connector = connector
        self.table_name = table_name
        self.primary_key = primary_key

    def write(self, df: DataFrame | ChangeSet, chunk_size: int | None = None) -> None:
        write_df = _as_dataframe(df)
        if write_df.empty:
            print("No rows to write")
            return
        self._validate_input(write_df)
        engine = self.connector.connect()
        self._write(engine, write_df, chunk_size=chunk_size)

    def _validate_input(self, frame: DataFrame) -> None:
        if self.requires_primary_key():
            if not self.primary_key:
                raise ValueError("primary_key is required")
            if self.primary_key not in frame.columns:
                raise ValueError(f"Primary key column '{self.primary_key}' not found in dataframe")

    def requires_primary_key(self) -> bool:
        return False

    @abstractmethod
    def _write(self, engine, df: DataFrame, chunk_size: int | None) -> None:
        raise NotImplementedError


class BigQueryReplaceWriteStrategy(BigQueryBaseWriteStrategy):
    def _write(self, engine, df: DataFrame, chunk_size: int | None) -> None:
        self.connector.ensure_target_table(df, self.table_name)
        tgt = self.connector.qualified_table(self.table_name)
        managed = self.connector.require_existing_table or self.connector.uses_managed_ddl()
        if managed:
            with engine.begin() as conn:
                conn.execute(text(f"TRUNCATE TABLE {tgt}"))
            df.to_sql(self.table_name, engine, if_exists="append", index=False, chunksize=chunk_size)
        else:
            df.to_sql(self.table_name, engine, if_exists="replace", index=False, chunksize=chunk_size)
        print(f"Replaced BigQuery table {tgt} rows={len(df)}")


class BigQueryAppendWriteStrategy(BigQueryBaseWriteStrategy):
    def _write(self, engine, df: DataFrame, chunk_size: int | None) -> None:
        self.connector.ensure_target_table(df, self.table_name)
        tgt = self.connector.qualified_table(self.table_name)
        df.to_sql(self.table_name, engine, if_exists="append", index=False, chunksize=chunk_size)
        print(f"Appended into BigQuery table {tgt} rows={len(df)}")


class BigQueryMergeWriteStrategy(BigQueryBaseWriteStrategy):
    """Stage rows into a temp table, then ``MERGE`` into the target by primary key."""

    def requires_primary_key(self) -> bool:
        return True

    def _merge_statement(self, staging_name: str, columns: list[str]) -> str:
        pk = self.primary_key
        assert pk is not None
        target_fqn = self.connector.qualified_table(self.table_name)
        staging_fqn = self.connector.qualified_table(staging_name)

        update_cols = [c for c in columns if c != pk]
        if not update_cols:
            update_clause = f"T.`{pk}` = S.`{pk}`"
        else:
            update_clause = ", ".join(f"T.`{c}` = S.`{c}`" for c in update_cols)

        insert_cols = ", ".join(f"`{c}`" for c in columns)
        insert_vals = ", ".join(f"S.`{c}`" for c in columns)

        return f"""
MERGE {target_fqn} AS T
USING {staging_fqn} AS S
ON T.`{pk}` = S.`{pk}`
WHEN MATCHED THEN UPDATE SET {update_clause}
WHEN NOT MATCHED THEN INSERT ({insert_cols}) VALUES ({insert_vals})
"""

    def _write(self, engine, df: DataFrame, chunk_size: int | None) -> None:
        self.connector.ensure_target_table(df, self.table_name)
        staging = f"{self.table_name}_etl_stg_{uuid.uuid4().hex[:10]}"
        tgt = self.connector.qualified_table(self.table_name)
        try:
            df.to_sql(staging, engine, if_exists="replace", index=False, chunksize=chunk_size)
            sql = self._merge_statement(staging, list(df.columns))
            with engine.begin() as conn:
                conn.execute(text(sql))
            print(f"Merged into BigQuery table {tgt} rows={len(df)}")
        finally:
            drop_sql = text(f"DROP TABLE IF EXISTS {self.connector.qualified_table(staging)}")
            with engine.begin() as conn:
                conn.execute(drop_sql)
