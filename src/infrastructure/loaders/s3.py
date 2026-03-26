from io import StringIO

import pandas as pd

from src.domain.contracts.loader import BaseLoader
from src.infrastructure.connectors.s3 import S3Connector


class S3CsvLoader(BaseLoader):
    def __init__(self, connector: S3Connector, key: str):
        self.connector = connector
        self.key = key

    def load(self, df: pd.DataFrame, chunk_size: int | None = None) -> None:
        s3 = self.connector.connect()
        buf = StringIO()
        df.to_csv(buf, index=False)
        s3.put_object(
            Bucket=self.connector.bucket_name,
            Key=self.key,
            Body=buf.getvalue().encode("utf-8"),
            ContentType="text/csv",
        )
