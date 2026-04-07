"""Base classes and shared helpers for Postgres SQL write strategies."""

from __future__ import annotations

from abc import abstractmethod

from pandas import DataFrame
from sqlalchemy import inspect, text

from src.domain.contracts.write_strategy import BaseWriteStrategy
from src.domain.models.change_set import ChangeSet
from src.infrastructure.utils.postgres_staging import build_dtype_map, stage_dataframe


class BasePostgresSQLWriter(BaseWriteStrategy):
    """Base class for writers that stage dataframes and write into Postgres."""
    def __init__(
        self,
        connector,
        table_name: str,
        primary_key: str | None = None,
    ):
        self.connector = connector
        self.table_name = table_name
        self.temp_table_name = f"{table_name}_temp"
        self.primary_key = primary_key

    def write(self, df: DataFrame | ChangeSet, chunk_size: int | None = None) -> None:
        write_df = self._coerce_to_dataframe(df)
        if write_df.empty:
            print("No rows to write")
            return

        self._validate_input(write_df)
        engine, _ = self._stage_dataframe(write_df, chunk_size=chunk_size)

        try:
            if not self._target_exists(engine):
                self._initialize_target(engine, write_df)
                return

            self._write_to_existing_target(engine, write_df)
        finally:
            self._drop_temp_table(engine)

    def _coerce_to_dataframe(self, df: DataFrame | ChangeSet) -> DataFrame:
        if isinstance(df, ChangeSet):
            return df.rows_to_write
        return df

    def _validate_input(self, df: DataFrame) -> None:
        if self.requires_primary_key() and self.primary_key not in df.columns:
            raise ValueError(
                f"Primary key column '{self.primary_key}' not found in dataframe"
            )

    def requires_primary_key(self) -> bool:
        """Whether this writer requires a primary key column in the input."""
        return False

    def _dtype_map(self, df: DataFrame) -> dict:
        return build_dtype_map(df)

    @staticmethod
    def stage_dataframe_to_table(
        *,
        engine,
        df: DataFrame,
        temp_table_name: str,
        chunk_size: int | None = None,
    ) -> None:
        """Stage a dataframe into a Postgres temp table.

        Centralized helper to prevent copy/paste of the staging call across
        multiple writers/loaders.
        """

        stage_dataframe(
            df=df,
            engine=engine,
            temp_table_name=temp_table_name,
            chunk_size=chunk_size,
        )

    def _stage_dataframe(self, df: DataFrame, chunk_size: int | None = None):
        engine = self.connector.connect()
        dtype_map = self._dtype_map(df)
        self.stage_dataframe_to_table(
            engine=engine,
            df=df,
            temp_table_name=self.temp_table_name,
            chunk_size=chunk_size,
        )
        return engine, dtype_map

    def _target_exists(self, engine) -> bool:
        return inspect(engine).has_table(self.table_name)

    def _drop_temp_table(self, engine) -> None:
        with engine.begin() as conn:
            conn.execute(text(f'DROP TABLE IF EXISTS "{self.temp_table_name}"'))

    def _rename_temp_to_target(self, engine) -> None:
        with engine.begin() as conn:
            self._rename_table(conn, self.temp_table_name, self.table_name)

    def _rename_table(self, conn, source_table_name: str, target_table_name: str) -> None:
        conn.execute(
            text(
                f'ALTER TABLE "{source_table_name}" '
                f'RENAME TO "{target_table_name}"'
            )
        )

    def _replace_target_with_staged(self, conn) -> None:
        conn.execute(text(f'DROP TABLE IF EXISTS "{self.table_name}"'))
        self._rename_table(conn, self.temp_table_name, self.table_name)

    def _delete_duplicate_rows(self, conn, table_name: str) -> None:
        if not self.primary_key:
            return

        conn.execute(
            text(
                f'''
                DELETE FROM "{table_name}"
                WHERE ctid NOT IN (
                    SELECT MIN(ctid)
                    FROM "{table_name}"
                    GROUP BY "{self.primary_key}"
                )
                '''
            )
        )

    def _ensure_unique_index(self, conn, table_name: str) -> None:
        if not self.primary_key:
            return

        index_name = self._build_unique_index_name(table_name, self.primary_key)
        conn.execute(
            text(
                f'CREATE UNIQUE INDEX IF NOT EXISTS "{index_name}" '
                f'ON "{table_name}" ("{self.primary_key}")'
            )
        )

    def _build_unique_index_name(self, table_name: str, column_name: str) -> str:
        return f"ux_{table_name}_{column_name}"

    def _build_index_name(self, table_name: str, columns: list[str]) -> str:
        return f'ix_{table_name}_{"_".join(columns)}'

    def _initialize_target(self, engine, df: DataFrame) -> None:
        self._rename_temp_to_target(engine)
        print(f"Initialized '{self.table_name}' with {len(df)} rows")

    @abstractmethod
    def _write_to_existing_target(self, engine, df: DataFrame) -> None:
        raise NotImplementedError


class PrimaryKeyPostgresSQLWriter(BasePostgresSQLWriter):
    """Writer base that enforces the presence of a primary key in input data."""

    def __init__(self, connector, table_name: str, primary_key: str):
        super().__init__(
            connector=connector,
            table_name=table_name,
            primary_key=primary_key,
        )

    def requires_primary_key(self) -> bool:
        return True
