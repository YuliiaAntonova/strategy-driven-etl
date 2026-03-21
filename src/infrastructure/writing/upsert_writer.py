from pandas import DataFrame
from sqlalchemy import text

from src.domain.contracts.write_strategy import BaseWriteStrategy
from src.infrastructure.writing.sql_writer_base import BasePostgresSQLWriter


class UpsertWriteStrategy(BaseWriteStrategy, BasePostgresSQLWriter):
    def __init__(self, connector, table_name: str, primary_key: str):
        BasePostgresSQLWriter.__init__(self, connector=connector, table_name=table_name)
        self.primary_key = primary_key

    def write(self, df: DataFrame, chunk_size: int | None = None) -> None:
        if df.empty:
            print("No rows to write")
            return
        if self.primary_key not in df.columns:
            raise ValueError(f"Primary key column '{self.primary_key}' not found in dataframe")
        engine, _ = self._stage_dataframe(df, chunk_size=chunk_size)
        if not self._target_exists(engine):
            with engine.begin() as conn:
                conn.execute(text(f'ALTER TABLE "{self.temp_table_name}" RENAME TO "{self.table_name}"'))
                conn.execute(text(
                    f'CREATE UNIQUE INDEX IF NOT EXISTS "ux_{self.table_name}_{self.primary_key}" ON "{self.table_name}" ("{self.primary_key}")'
                ))
            print(f"Initialized '{self.table_name}' from staging '{self.temp_table_name}'")
            return
        cols = list(df.columns)
        insert_cols = ", ".join(f'"{c}"' for c in cols)
        select_cols = ", ".join(f's."{c}"' for c in cols)
        update_cols = [c for c in cols if c != self.primary_key]
        update_set = ", ".join(f'"{c}" = EXCLUDED."{c}"' for c in update_cols)
        sql = text(
            f'''INSERT INTO "{self.table_name}" ({insert_cols})
                SELECT {select_cols}
                FROM "{self.temp_table_name}" s
                ON CONFLICT ("{self.primary_key}") DO UPDATE
                SET {update_set}'''
        )
        with engine.begin() as conn:
            conn.execute(text(
                f'CREATE UNIQUE INDEX IF NOT EXISTS "ux_{self.table_name}_{self.primary_key}" ON "{self.table_name}" ("{self.primary_key}")'
            ))
            result = conn.execute(sql)
            conn.execute(text(f'DROP TABLE IF EXISTS "{self.temp_table_name}"'))
        print(f"Upserted {result.rowcount} rows into '{self.table_name}' from staging '{self.temp_table_name}'")
