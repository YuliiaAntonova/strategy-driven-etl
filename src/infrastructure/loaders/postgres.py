from pandas import DataFrame
from sqlalchemy import String, Text, Float, Integer, DateTime, Boolean

from src.domain.contracts.loader import BaseLoader
from src.infrastructure.connectors.postgres import PostgreSQLConnector


class PostgresLoader(BaseLoader):
    def __init__(self, connector: PostgreSQLConnector, table_name: str, if_exists: str = "replace"):
        self.connector = connector
        self.table_name = table_name
        self.if_exists = if_exists

    def load(self, df: DataFrame) -> None:
        engine = self.connector.connect()

        dtype_map = {
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

        df.to_sql(
            name=self.table_name,
            con=engine,
            if_exists=self.if_exists,
            index=False,
            dtype={k: v for k, v in dtype_map.items() if k in df.columns},
        )

        print(f"Loaded {len(df)} rows into table '{self.table_name}' with mode '{self.if_exists}'")