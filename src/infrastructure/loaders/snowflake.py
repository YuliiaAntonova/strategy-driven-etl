"""Loader for persisting pandas dataframes to Snowflake.

Note: This implementation assumes the connector returns a SQLAlchemy Engine.
"""

import pandas as pd
from src.domain.contracts.loader import BaseLoader


class PandasToSnowflakeLoader(BaseLoader):
    """Append dataframe rows into a Snowflake table."""

    def __init__(self, connector, table_name):
        self.connector = connector
        self.table_name = table_name

    def load(self, df: pd.DataFrame, chunk_size: int | None = None) -> None:
        conn = self.connector.connect()
        try:
            df.to_sql(
                name=self.table_name,
                con=conn,
                if_exists="append",
                index=False,
                method="multi",
                chunksize=chunk_size,
            )
        finally:
            conn.dispose()
