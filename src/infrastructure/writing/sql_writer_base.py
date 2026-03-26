from __future__ import annotations

from abc import abstractmethod

from pandas import DataFrame
from sqlalchemy import inspect, text

from src.domain.contracts.write_strategy import BaseWriteStrategy
from src.infrastructure.utils.jobs_dtype import JOBS_DTYPE_MAP
from src.infrastructure.utils.temp_table import stage_dataframe_to_temp


class BasePostgresSQLWriter(BaseWriteStrategy):
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

    def write(self, df: DataFrame, chunk_size: int | None = None) -> None:
        if df.empty:
            print("No rows to write")
            return

        self._validate_input(df)
        engine, _ = self._stage_dataframe(df, chunk_size=chunk_size)

        try:
            if not self._target_exists(engine):
                self._initialize_target(engine, df)
                return

            self._write_to_existing_target(engine, df)
        finally:
            self._drop_temp_table(engine)

    def _validate_input(self, df: DataFrame) -> None:
        if self.requires_primary_key() and self.primary_key not in df.columns:
            raise ValueError(
                f"Primary key column '{self.primary_key}' not found in dataframe"
            )

    def requires_primary_key(self) -> bool:
        return False

    def _dtype_map(self) -> dict:
        return JOBS_DTYPE_MAP

    def _stage_dataframe(self, df: DataFrame, chunk_size: int | None = None):
        engine = self.connector.connect()
        dtype_map = {key: value for key, value in self._dtype_map().items() if key in df.columns}

        stage_dataframe_to_temp(
            df=df,
            engine=engine,
            temp_table_name=self.temp_table_name,
            dtype_map=dtype_map,
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
            conn.execute(
                text(
                    f'ALTER TABLE "{self.temp_table_name}" '
                    f'RENAME TO "{self.table_name}"'
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
        """Apply strategy-specific SQL against an existing target table."""
