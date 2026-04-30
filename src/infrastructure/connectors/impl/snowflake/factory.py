from __future__ import annotations

from src.infrastructure.connectors.base.capabilities import ConnectorCapabilities
from src.infrastructure.connectors.base.factory import BaseConnectorFactory
from src.infrastructure.connectors.snowflake__connector import SnowflakeConnector
from src.infrastructure.extractors.sql import SQLExtractor


class SnowflakeConnectorFactory(BaseConnectorFactory):
    capabilities = ConnectorCapabilities(
        supports_extractor=True,
        supports_loader=True,
    )

    def _connector(self, credentials):
        return SnowflakeConnector(
            account=credentials["account"],
            user=credentials["user"],
            password=credentials["password"],
            warehouse=credentials["warehouse"],
            database=credentials["database"],
            schema=credentials["schema"],
            role=credentials.get("role"),
        )

    def create_extractor(self, source_spec, credentials):
        query = source_spec.config.get("query")

        if not query:
            raise ValueError("snowflake extractor requires config.query")

        return SQLExtractor(
            connector=self._connector(credentials),
            query=query,
        )

    def create_loader(self, destination_spec, credentials):
        return self._connector(credentials)