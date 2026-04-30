from __future__ import annotations

from src.infrastructure.connectors.base.capabilities import ConnectorCapabilities
from src.infrastructure.connectors.base.factory import BaseConnectorFactory
from src.infrastructure.connectors.postgres import PostgreSQLConnector
from src.infrastructure.extractors.sql import SQLExtractor


class PostgresConnectorFactory(BaseConnectorFactory):
    capabilities = ConnectorCapabilities(
        supports_extractor=True,
        supports_loader=True,
    )

    def _connector(self, credentials):
        return PostgreSQLConnector(
            host=credentials["host"],
            database=credentials["database"],
            user=credentials["user"],
            password=credentials["password"],
            port=int(credentials.get("port", 5432)),
        )

    def create_extractor(self, source_spec, credentials):
        query = source_spec.config.get("query")

        if not query:
            raise ValueError("postgres extractor requires config.query")

        return SQLExtractor(
            connector=self._connector(credentials),
            query=query,
        )

    def create_loader(self, destination_spec, credentials):
        return self._connector(credentials)