from __future__ import annotations

from typing import Any

from src.application.runtime.keyed_registry import KeyedRegistry


class ConnectorRegistry(KeyedRegistry[Any]):
    def __init__(self) -> None:
        super().__init__(entity_label="connector type")

    def build_extractor(self, source_spec, credentials):
        factory = self.require(source_spec.type)

        if not factory.capabilities.supports_extractor:
            raise ValueError(f"Connector '{source_spec.type}' does not support extractor role")

        return factory.create_extractor(source_spec, credentials)

    def build_loader(self, destination_spec, credentials):
        factory = self.require(destination_spec.type)

        if not factory.capabilities.supports_loader:
            raise ValueError(f"Connector '{destination_spec.type}' does not support loader role")

        return factory.create_loader(destination_spec, credentials)
