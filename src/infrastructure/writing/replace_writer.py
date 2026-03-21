from pandas import DataFrame
from sqlalchemy import text

from src.domain.contracts.write_strategy import BaseWriteStrategy
from src.infrastructure.writing.sql_writer_base import BasePostgresSQLWriter


class ReplaceWriteStrategy(BaseWriteStrategy, BasePostgresSQLWriter):
    def __init__(self, connector, table_name: str):
        BasePostgresSQLWriter.__init__(self, connector=connector, table_name=table_name)

    def write(self, df: DataFrame, chunk_size: int | None = None) -> None:
        if df.empty:
            print("No rows to write")
            return
        engine, _ = self._stage_dataframe(df, chunk_size=chunk_size)
        with engine.begin() as conn:
            conn.execute(text(f'DROP TABLE IF EXISTS "{self.table_name}"'))
            conn.execute(text(f'ALTER TABLE "{self.temp_table_name}" RENAME TO "{self.table_name}"'))
        print(f"Replaced '{self.table_name}' from staging '{self.temp_table_name}' with {len(df)} rows")
