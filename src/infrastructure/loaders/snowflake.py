import pandas as pd
from src.domain.contracts.loader import BaseLoader

class PandasToSnowflakeLoader(BaseLoader):
    def __init__(self, connector, table_name):
        self.connector = connector
        self.table_name = table_name

    def load(self, df: pd.DataFrame):
        conn = self.connector.connect()
        try:
            df.to_sql(
                name=self.table_name,
                con=conn,
                if_exists="append",
                index=False,
                method="multi",
            )
        finally:
            conn.dispose()
