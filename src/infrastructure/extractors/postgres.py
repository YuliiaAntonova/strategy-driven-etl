import pandas as pd
from pandas import DataFrame

from src.domain.contracts.extractor import BaseExtractor
from src.infrastructure.connectors.postgres import PostgreSQLConnector


class PostgresExtractor(BaseExtractor):
    def __init__(self, connector: PostgreSQLConnector, query: str):
        self.connector = connector
        self.query = query

    def extract(self) -> DataFrame:
        engine = self.connector.connect()
        return pd.read_sql(self.query, con=engine)
