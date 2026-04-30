from sqlalchemy import create_engine

from src.domain.contracts.connector import BaseConnector


class PostgreSQLConnector(BaseConnector):
    def __init__(
        self,
        host: str,
        database: str,
        user: str,
        password: str,
        port: int = 5432,
    ):
        self.host = host
        self.database = database
        self.user = user
        self.password = password
        self.port = port
        self._engine = create_engine(
            (
                f"postgresql://{self.user}:{self.password}"
                f"@{self.host}:{self.port}/{self.database}"
            )
        )

    def connect(self):
        return self._engine
