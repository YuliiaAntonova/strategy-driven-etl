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


def build_destination_connector(destination_type: str, credentials: dict):
    if destination_type == "postgres":
        return PostgreSQLConnector(
            host=credentials["host"],
            database=credentials["database"],
            user=credentials["user"],
            password=credentials["password"],
            port=int(credentials.get("port", 5432)),
        )
    raise ValueError(f"Unsupported destination type: {destination_type}")
