from __future__ import annotations

from src.infrastructure.connectors.factory import build_destination_connector


def build_connector_from_spec(destination_spec, credentials):
    return build_destination_connector(
        destination_type=destination_spec.type,
        credentials=credentials,
    )


DESTINATION_FACTORIES = {
    "postgres": build_connector_from_spec,
}
