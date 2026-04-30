"""Shared write orchestration: SQLAlchemy engine, temp staging table, merge/replace."""

from __future__ import annotations

from abc import ABC, abstractmethod

from pandas import DataFrame
from sqlalchemy import inspect, text

from src.domain.contracts.write_strategy import BaseWriteStrategy
from src.domain.models.change_set import ChangeSet
from src.infrastructure.utils.postgres_staging import stage_dataframe


class StagedSqlTableWriter(BaseWriteStrategy, ABC):
    """Connect → stage to `{table}_temp` → branch on target existence → drop temp."""

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
        engine = self.connector.connect()

        try:
            stage_dataframe(
                df=write_df,
                engine=engine,
                temp_table_name=self.temp_table_name,
                chunk_size=chunk_size,
            )

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
        return False

    def _target_exists(self, engine) -> bool:
        return inspect(engine).has_table(self.table_name)

    def _drop_temp_table(self, engine) -> None:
        with engine.begin() as conn:
            conn.execute(text(f'DROP TABLE IF EXISTS "{self.temp_table_name}"'))

    def _rename_temp_to_target(self, engine) -> None:
        with engine.begin() as conn:
            conn.execute(
                text(
                    f'ALTER TABLE "{self.temp_table_name}" '
                    f'RENAME TO "{self.table_name}"'
                )
            )

    def _initialize_target(self, engine, df: DataFrame) -> None:
        self._rename_temp_to_target(engine)
        print(f"Initialized table '{self.table_name}' with {len(df)} rows")

    @abstractmethod
    def _write_to_existing_target(self, engine, df: DataFrame) -> None:
        raise NotImplementedError
