from __future__ import annotations


from src.infrastructure.connectors.postgres import PostgreSQLConnector


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
