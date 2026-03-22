from __future__ import annotations

from abc import abstractmethod

from pandas import DataFrame
from sqlalchemy import Boolean, DateTime, Float, Integer, String, Text, inspect, text

from src.domain.contracts.write_strategy import BaseWriteStrategy


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
        return {
            "job_url": Text(),
            "site": String(100),
            "title": Text(),
            "company": Text(),
            "location": Text(),
            "job_type": String(100),
            "date_posted": String(50),
            "interval": String(50),
            "min_amount": Float(),
            "max_amount": Float(),
            "currency": String(50),
            "is_remote": String(50),
            "num_urgent_words": Integer(),
            "benefits": Text(),
            "emails": Text(),
            "description": Text(),
            "source_name": String(100),
            "run_id": String(100),
            "dt": String(50),
            "date_created": DateTime(timezone=True),
            "date_loaded": DateTime(timezone=True),
            "environment": String(50),
            "row_hash": String(64),
            "is_current": Boolean(),
        }

    def _stage_dataframe(self, df: DataFrame, chunk_size: int | None = None):
        engine = self.connector.connect()
        dtype_map = {key: value for key, value in self._dtype_map().items() if key in df.columns}

        with engine.begin() as conn:
            conn.execute(text(f'DROP TABLE IF EXISTS "{self.temp_table_name}"'))

        df.to_sql(
            name=self.temp_table_name,
            con=engine,
            if_exists="replace",
            index=False,
            chunksize=chunk_size,
            dtype=dtype_map,
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
