from __future__ import annotations

from src.config.settings import settings
from src.infrastructure.connectors.postgres import PostgreSQLConnector


def get_postgres_connector(connector: PostgreSQLConnector | None = None) -> PostgreSQLConnector:
    if connector is not None:
        return connector

    return PostgreSQLConnector(
        host=settings.postgres_host,
        database=settings.postgres_db,
        user=settings.postgres_user,
        password=settings.postgres_password,
        port=settings.postgres_port,
    )
