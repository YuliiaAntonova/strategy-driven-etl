from pandas import DataFrame
from sqlalchemy import String, Text, Float, Integer, DateTime, Boolean, inspect, text


class BasePostgresSQLWriter:
    def __init__(self, connector, table_name: str):
        self.connector = connector
        self.table_name = table_name
        self.temp_table_name = f"{table_name}_temp"

    def _dtype_map(self) -> dict:
        return {
            "job_url": Text(),
            "site": String(100),
            "title": Text(),
            "company": Text(),
            "location": Text(),
            "job_type": String(100),
            "date_posted": String(50),
            "interval": String(50),
            "min_amount": Float(),
            "max_amount": Float(),
            "currency": String(50),
            "is_remote": String(50),
            "num_urgent_words": Integer(),
            "benefits": Text(),
            "emails": Text(),
            "description": Text(),
            "source_name": String(100),
            "run_id": String(100),
            "dt": String(50),
            "date_created": DateTime(timezone=True),
            "date_loaded": DateTime(timezone=True),
            "environment": String(50),
            "row_hash": String(64),
            "is_current": Boolean(),
        }

    def _stage_dataframe(self, df: DataFrame):
        engine = self.connector.connect()
        dtype_map = {k: v for k, v in self._dtype_map().items() if k in df.columns}
        with engine.begin() as conn:
            conn.execute(text(f'DROP TABLE IF EXISTS "{self.temp_table_name}"'))
        df.to_sql(
            name=self.temp_table_name,
            con=engine,
            if_exists="replace",
            index=False,
            dtype=dtype_map,
        )
        return engine, dtype_map

    def _target_exists(self, engine) -> bool:
        return inspect(engine).has_table(self.table_name)
