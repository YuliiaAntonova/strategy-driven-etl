from __future__ import annotations

from src.infrastructure.connectors.base.capabilities import ConnectorCapabilities
from src.infrastructure.connectors.base.factory import BaseConnectorFactory
from src.infrastructure.extractors.memory import MemoryExtractor


class MemoryConnectorFactory(BaseConnectorFactory):
    capabilities = ConnectorCapabilities(
        supports_extractor=True,
        supports_loader=False,
    )

    def create_extractor(self, source_spec, credentials):
        records = source_spec.config.get("records")

        if records is None:
            raise ValueError("memory extractor requires config.records")

        return MemoryExtractor(records=records)

    def create_loader(self, destination_spec, credentials):
        self._unsupported("memory", "loader")