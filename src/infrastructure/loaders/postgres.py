from pandas import DataFrame

from src.domain.contracts.loader import BaseLoader
from src.infrastructure.connectors.postgres import PostgreSQLConnector
from src.infrastructure.utils.jobs_dtype import JOBS_DTYPE_MAP


class PostgresLoader(BaseLoader):
    def __init__(self, connector: PostgreSQLConnector, table_name: str, if_exists: str = "replace"):
        self.connector = connector
        self.table_name = table_name
        self.if_exists = if_exists

    def load(self, df: DataFrame, chunk_size: int | None = None) -> None:
        engine = self.connector.connect()
        dtype_map = {k: v for k, v in JOBS_DTYPE_MAP.items() if k in df.columns}

        df.to_sql(
            name=self.table_name,
            con=engine,
            if_exists=self.if_exists,
            index=False,
            chunksize=chunk_size,
            dtype=dtype_map,
        )

        print(
            f"Loaded {len(df)} rows into table '{self.table_name}' "
            f"with mode '{self.if_exists}'"
        )