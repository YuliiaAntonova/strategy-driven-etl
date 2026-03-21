import pandas as pd
from pandas import DataFrame
from typing import Iterator

from src.domain.contracts.extractor import BaseExtractor


class CSVExtractor(BaseExtractor):
    def __init__(self, file_path: str):
        self.file_path = file_path

    def extract(self) -> DataFrame:
        return pd.read_csv(self.file_path)

    def extract_in_chunks(self, chunk_size: int) -> Iterator[DataFrame]:
        yield from pd.read_csv(self.file_path, chunksize=chunk_size)