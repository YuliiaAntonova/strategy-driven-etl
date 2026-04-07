"""Transformer that computes a stable row hash from selected columns."""

import hashlib

from pandas import DataFrame

from src.domain.contracts.transformer import BaseTransformer


class HashColumnsTransformer(BaseTransformer):
    """Add a hash column computed from the configured list of columns."""

    def __init__(self, columns: list[str], output_column: str = "row_hash"):
        self.columns = columns
        self.output_column = output_column

    def transform(self, df: DataFrame) -> DataFrame:
        result = df.copy()

        missing_columns = [
            column for column in self.columns if column not in result.columns
        ]
        if missing_columns:
            raise ValueError(f"Missing columns for hash calculation: {missing_columns}")

        def _hash_row(row) -> str:
            raw = "||".join(
                "" if row[column] is None else str(row[column])
                for column in self.columns
            )
            return hashlib.md5(raw.encode("utf-8")).hexdigest()

        result[self.output_column] = result.apply(_hash_row, axis=1)
        return result
