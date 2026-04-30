from __future__ import annotations

from sqlalchemy import create_engine
from snowflake.sqlalchemy import URL

from src.domain.contracts.connector import BaseConnector


class SnowflakeConnector(BaseConnector):
    def __init__(
        self,
        *,
        account: str,
        user: str,
        password: str,
        warehouse: str,
        database: str,
        schema: str,
        role: str | None = None,
    ):
        self._engine = create_engine(
            URL(
                account=account,
                user=user,
                password=password,
                warehouse=warehouse,
                database=database,
                schema=schema,
                role=role,
            )
        )

    def connect(self):
        return self._engine