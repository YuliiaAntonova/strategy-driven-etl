import pandas as pd
from pandas import DataFrame
from typing import Iterator

from src.domain.contracts.extractor import BaseExtractor
from src.infrastructure.connectors.postgres import PostgreSQLConnector


class PostgresExtractor(BaseExtractor):
    def __init__(self, connector: PostgreSQLConnector, query: str):
        self.connector = connector
        self.query = query

    def extract(self) -> DataFrame:
        engine = self.connector.connect()
        return pd.read_sql(self.query, con=engine)

    def extract_in_chunks(self, chunk_size: int) -> Iterator[DataFrame]:
        engine = self.connector.connect()
        yield from pd.read_sql(self.query, con=engine, chunksize=chunk_size)