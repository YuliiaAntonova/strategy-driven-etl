from __future__ import annotations

from src.infrastructure.connectors.base.capabilities import ConnectorCapabilities
from src.infrastructure.connectors.base.factory import BaseConnectorFactory
from src.infrastructure.extractors.csv import CSVExtractor


class CsvConnectorFactory(BaseConnectorFactory):
    capabilities = ConnectorCapabilities(
        supports_extractor=True,
        supports_loader=False,
    )

    def create_extractor(self, source_spec, credentials):
        file_path = source_spec.config.get("file_path")

        if not file_path:
            raise ValueError("csv extractor requires config.file_path")

        return CSVExtractor(file_path=file_path)

    def create_loader(self, destination_spec, credentials):
        self._unsupported("csv", "loader")