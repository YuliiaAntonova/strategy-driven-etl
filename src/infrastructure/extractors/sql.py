from __future__ import annotations

from typing import Iterator

import pandas as pd
from pandas import DataFrame

from src.domain.contracts.extractor import BaseExtractor


class SQLExtractor(BaseExtractor):
    def __init__(self, connector, query: str):
        self.connector = connector
        self.query = query

    def extract(self) -> DataFrame:
        engine = self.connector.connect()
        return pd.read_sql(self.query, con=engine)

    def extract_in_chunks(self, chunk_size: int) -> Iterator[DataFrame]:
        engine = self.connector.connect()
        yield from pd.read_sql(self.query, con=engine, chunksize=chunk_size)