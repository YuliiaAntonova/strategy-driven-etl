from __future__ import annotations

from abc import ABC, abstractmethod

from src.infrastructure.connectors.base.capabilities import ConnectorCapabilities


class BaseConnectorFactory(ABC):
    capabilities = ConnectorCapabilities()

    @abstractmethod
    def create_extractor(self, source_spec, credentials):
        raise NotImplementedError

    @abstractmethod
    def create_loader(self, destination_spec, credentials):
        raise NotImplementedError

    def _unsupported(self, connector_type: str, role: str):
        raise ValueError(f"Connector '{connector_type}' does not support role '{role}'")