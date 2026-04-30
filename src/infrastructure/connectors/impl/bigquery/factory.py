from __future__ import annotations

from src.infrastructure.connectors.base.capabilities import ConnectorCapabilities
from src.infrastructure.connectors.base.factory import BaseConnectorFactory
from src.infrastructure.connectors.bigquery_connector import BigQueryConnector
from src.infrastructure.extractors.sql import SQLExtractor


class BigQueryConnectorFactory(BaseConnectorFactory):
    capabilities = ConnectorCapabilities(
        supports_extractor=True,
        supports_loader=True,
    )

    def _connector(self, credentials: dict) -> BigQueryConnector:
        return BigQueryConnector(
            project_id=credentials["project_id"],
            dataset=credentials["dataset"],
            credentials_path=credentials.get("credentials_path"),
            location=credentials.get("location"),
        )

    def create_extractor(self, source_spec, credentials):
        query = source_spec.config.get("query")
        if not query:
            raise ValueError("bigquery extractor requires config.query")
        return SQLExtractor(
            connector=self._connector(credentials),
            query=query,
        )

    def create_loader(self, destination_spec, credentials):
        connector = self._connector(credentials)
        connector.bind_destination_spec(destination_spec.config)
        return connector
