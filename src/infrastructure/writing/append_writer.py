from pandas import DataFrame
from sqlalchemy import text

from src.domain.contracts.write_strategy import BaseWriteStrategy
from src.infrastructure.writing.sql_writer_base import BasePostgresSQLWriter


class AppendWriteStrategy(BaseWriteStrategy, BasePostgresSQLWriter):
    def __init__(self, connector, table_name: str):
        BasePostgresSQLWriter.__init__(self, connector=connector, table_name=table_name)

    def write(self, df: DataFrame, chunk_size: int | None = None) -> None:
        if df.empty:
            print("No rows to write")
            return
        engine, _ = self._stage_dataframe(df, chunk_size=chunk_size)
        if not self._target_exists(engine):
            with engine.begin() as conn:
                conn.execute(text(f'ALTER TABLE "{self.temp_table_name}" RENAME TO "{self.table_name}"'))
            print(f"Initialized '{self.table_name}' from staging '{self.temp_table_name}'")
            return
        columns = [f'"{c}"' for c in df.columns]
        sql = text(
            f'''INSERT INTO "{self.table_name}" ({", ".join(columns)})
                SELECT {", ".join(columns)} FROM "{self.temp_table_name}"'''
        )
        with engine.begin() as conn:
            result = conn.execute(sql)
            conn.execute(text(f'DROP TABLE IF EXISTS "{self.temp_table_name}"'))
        print(f"Appended {result.rowcount} rows into '{self.table_name}' from staging '{self.temp_table_name}'")
