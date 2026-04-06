from __future__ import annotations

from pandas import DataFrame

from src.infrastructure.utils.jobs_dtype import JOBS_DTYPE_MAP
from src.infrastructure.utils.temp_table import stage_dataframe_to_temp


def build_dtype_map(df: DataFrame) -> dict:
    return {key: value for key, value in JOBS_DTYPE_MAP.items() if key in df.columns}


def stage_dataframe(df: DataFrame, engine, temp_table_name: str, chunk_size: int | None = None) -> dict:
    dtype_map = build_dtype_map(df)
    stage_dataframe_to_temp(
        df=df,
        engine=engine,
        temp_table_name=temp_table_name,
        dtype_map=dtype_map,
        chunk_size=chunk_size,
    )
    return dtype_map
