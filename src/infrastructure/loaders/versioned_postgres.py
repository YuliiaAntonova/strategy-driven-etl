from pandas import DataFrame
from sqlalchemy import String, Text, Float, Integer, DateTime, Boolean, text, inspect

from src.domain.contracts.loader import BaseLoader
from src.infrastructure.connectors.postgres import PostgreSQLConnector


class VersionedPostgresLoader(BaseLoader):
    def __init__(
        self,
        connector: PostgreSQLConnector,
        table_name: str,
        primary_key: str,
    ):
        self.connector = connector
        self.table_name = table_name
        self.primary_key = primary_key
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

    def load(self, df: DataFrame) -> None:
        if df.empty:
            print("No rows to load")
            return

        if self.primary_key not in df.columns:
            raise ValueError(f"Primary key column '{self.primary_key}' not found in dataframe")

        engine = self.connector.connect()
        dtype_map = {k: v for k, v in self._dtype_map().items() if k in df.columns}

        # Always land the incoming batch into a staging table named {table_name}_temp.
        df.to_sql(
            name=self.temp_table_name,
            con=engine,
            if_exists="replace",
            index=False,
            dtype=dtype_map,
        )

        inspector = inspect(engine)
        target_exists = inspector.has_table(self.table_name)

        # Initialize the target table on the first run.
        if not target_exists:
            df.to_sql(
                name=self.table_name,
                con=engine,
                if_exists="replace",
                index=False,
                dtype=dtype_map,
            )
            with engine.begin() as conn:
                conn.execute(text(f'DROP TABLE IF EXISTS "{self.temp_table_name}"'))
            print(f"Initialized '{self.table_name}' from staging table '{self.temp_table_name}'")
            print(f"Loaded {len(df)} versioned rows into table '{self.table_name}'")
            return

        quoted_columns = [f'"{column}"' for column in df.columns]
        select_columns = []
        for column in df.columns:
            if column == "date_created":
                select_columns.append('COALESCE(lt."date_created", s."date_created") AS "date_created"')
            else:
                select_columns.append(f's."{column}"')

        dedup_staging_cte = f"""
            WITH staged AS (
                SELECT *
                FROM (
                    SELECT
                        s.*,
                        ROW_NUMBER() OVER (
                            PARTITION BY s."{self.primary_key}"
                            ORDER BY s."date_loaded" DESC NULLS LAST
                        ) AS rn
                    FROM "{self.temp_table_name}" s
                ) ranked
                WHERE ranked.rn = 1
            ),
            latest_target AS (
                SELECT DISTINCT ON (t."{self.primary_key}")
                    t.*
                FROM "{self.table_name}" t
                ORDER BY t."{self.primary_key}", t."date_loaded" DESC NULLS LAST
            )
        """

        update_sql = text(
            dedup_staging_cte
            + f"""
            UPDATE "{self.table_name}" t
            SET "is_current" = false
            FROM staged s
            WHERE t."{self.primary_key}" = s."{self.primary_key}"
              AND t."is_current" = true
              AND COALESCE(t."row_hash", '') <> COALESCE(s."row_hash", '')
            """
        )

        insert_sql = text(
            dedup_staging_cte
            + f"""
            INSERT INTO "{self.table_name}" ({", ".join(quoted_columns)})
            SELECT {", ".join(select_columns)}
            FROM staged s
            LEFT JOIN latest_target lt
              ON lt."{self.primary_key}" = s."{self.primary_key}"
            WHERE lt."{self.primary_key}" IS NULL
               OR COALESCE(lt."row_hash", '') <> COALESCE(s."row_hash", '')
            """
        )

        with engine.begin() as conn:
            updated_result = conn.execute(update_sql)
            inserted_result = conn.execute(insert_sql)
            conn.execute(text(f'DROP TABLE IF EXISTS "{self.temp_table_name}"'))

        print(f"Closed previous current versions for {updated_result.rowcount} rows")
        print(
            f"Inserted {inserted_result.rowcount} rows into table '{self.table_name}' "
            f"from staging '{self.temp_table_name}'"
        )
