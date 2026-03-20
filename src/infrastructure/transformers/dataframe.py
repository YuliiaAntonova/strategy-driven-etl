from pandas import DataFrame

from src.domain.contracts.transformer import BaseTransformer


class RenameColumnsTransformer(BaseTransformer):
    def __init__(self, mapping: dict[str, str]):
        self.mapping = mapping

    def transform(self, df: DataFrame) -> DataFrame:
        return df.rename(columns=self.mapping)
