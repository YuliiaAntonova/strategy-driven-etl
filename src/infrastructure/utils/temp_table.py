from __future__ import annotations

from typing import Any

from pandas import DataFrame
from sqlalchemy import text


def stage_dataframe_to_temp(
    df: DataFrame,
    engine: Any,
    temp_table_name: str,
    dtype_map: dict,
    chunk_size: int | None = None,
) -> None:
    """Stage a dataframe into a temporary table `{temp_table_name}`.

    Drops the temp table if it exists and writes the dataframe with `if_exists="replace"`.
    """
    with engine.begin() as conn:
        conn.execute(text(f'DROP TABLE IF EXISTS "{temp_table_name}"'))

    df.to_sql(
        name=temp_table_name,
        con=engine,
        if_exists="replace",
        index=False,
        chunksize=chunk_size,
        dtype=dtype_map,
    )
