"""Composite transformer that applies multiple transformers sequentially."""

from __future__ import annotations

from pandas import DataFrame

from src.domain.contracts.transformer import BaseTransformer


class CompositeTransformer(BaseTransformer):
    """Apply a list of transformers in order."""

    def __init__(self, transformers: list[BaseTransformer]):
        self.transformers = transformers

    def transform(self, df: DataFrame) -> DataFrame:
        transformed = df.copy()
        for transformer in self.transformers:
            transformed = transformer.transform(transformed)
        return transformed
