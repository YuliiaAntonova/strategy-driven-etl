# Extensibility

## Add a new connector (source and/or destination)

1. Implement `BaseConnectorFactory` under `src/infrastructure/connectors/impl/<name>/factory.py`
   (`create_extractor` / `create_loader`, `ConnectorCapabilities`).
2. Register the factory instance in `src/infrastructure/connectors/catalog.py` (`CONNECTOR_FACTORIES`).
3. Backends with extra drivers (e.g. BigQuery): install option group ``pip install -e ".[bigquery]"``.

Connection YAML profiles live in `config/connectors.yml`.

## Add a new transform

Register the factory in `src/infrastructure/transformers/catalog.py` (`TRANSFORM_FACTORIES`).

## Wire detector / writer modes

- Detectors: `src/application/pipeline/registry.py` (`DETECTOR_FACTORIES`).
- Writers per backend: `src/application/pipeline/writer_dispatch.py` (`_WRITER_CLASSES`) and optional profile in `profiles.py`.

No changes are required in `test.py` unless you add a new runnable entrypoint.
