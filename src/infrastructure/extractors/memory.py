"""In-memory extractor for lists, iterables and decorator-based resources."""

from __future__ import annotations

from collections.abc import Iterable, Iterator

import pandas as pd
from pandas import DataFrame

from src.domain.contracts.extractor import BaseExtractor


class MemoryExtractor(BaseExtractor):
    def __init__(self, records: Iterable[dict] | list[dict]):
        self.records = records

    def _iter_records(self) -> Iterator[dict]:
        for item in self.records:
            if isinstance(item, DataFrame):
                yield from item.to_dict(orient="records")
            elif isinstance(item, list):
                for nested in item:
                    if not isinstance(nested, dict):
                        raise TypeError("MemoryExtractor list batches must contain dict rows")
                    yield nested
            elif isinstance(item, dict):
                yield item
            else:
                raise TypeError(f"Unsupported record type: {type(item)!r}")

    def extract(self) -> DataFrame:
        return pd.DataFrame(list(self._iter_records()))

    def extract_in_chunks(self, chunk_size: int):
        batch: list[dict] = []
        for record in self._iter_records():
            batch.append(record)
            if len(batch) >= chunk_size:
                yield pd.DataFrame(batch)
                batch = []
        if batch:
            yield pd.DataFrame(batch)
