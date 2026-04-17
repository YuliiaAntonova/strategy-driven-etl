from pandas import DataFrame

from src.domain.contracts.transformer import BaseTransformer


class IdentityTransformer(BaseTransformer):
    def transform(self, df: DataFrame) -> DataFrame:
        return df.copy()
