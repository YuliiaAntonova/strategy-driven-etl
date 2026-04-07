"""CSV extractor.

Reads a local CSV file into a pandas DataFrame. Can also stream the file in
chunks via pandas' iterator mode.
"""

from typing import Iterator

import pandas as pd
from pandas import DataFrame

from src.domain.contracts.extractor import BaseExtractor


class CSVExtractor(BaseExtractor):
    """Extract CSV data from the local filesystem."""

    def __init__(self, file_path: str):
        self.file_path = file_path

    def extract(self) -> DataFrame:
        return pd.read_csv(self.file_path)

    def extract_in_chunks(self, chunk_size: int) -> Iterator[DataFrame]:
        """Yield DataFrames of size `chunk_size` from the CSV file."""
        yield from pd.read_csv(self.file_path, chunksize=chunk_size)
