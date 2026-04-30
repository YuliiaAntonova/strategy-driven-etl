from __future__ import annotations

from src.infrastructure.connectors.base.capabilities import ConnectorCapabilities
from src.infrastructure.connectors.base.factory import BaseConnectorFactory
from src.infrastructure.extractors.jobs_api import JobsApiExtractor


class JobsApiConnectorFactory(BaseConnectorFactory):
    capabilities = ConnectorCapabilities(
        supports_extractor=True,
        supports_loader=False,
    )

    def create_extractor(self, source_spec, credentials):
        return JobsApiExtractor(
            search_term=source_spec.config["search_term"],
            location=source_spec.config["location"],
            results_wanted=source_spec.config.get("results_wanted", 100),
        )

    def create_loader(self, destination_spec, credentials):
        self._unsupported("jobs_api", "loader")