from __future__ import annotations

from src.infrastructure.connectors.factory import build_destination_connector
from src.infrastructure.extractors.csv import CSVExtractor
from src.infrastructure.extractors.jobs_api import JobsApiExtractor
from src.infrastructure.extractors.memory import MemoryExtractor
from src.infrastructure.extractors.postgres import PostgresExtractor


def build_memory_extractor(source_spec, credentials):
    records = source_spec.config.get("records")
    if records is None:
        raise ValueError("memory source requires config.records")
    return MemoryExtractor(records=records)


def build_csv_extractor(source_spec, credentials):
    file_path = source_spec.config.get("file_path")
    if not file_path:
        raise ValueError("csv source requires config.file_path")
    return CSVExtractor(file_path=file_path)


def build_jobs_api_extractor(source_spec, credentials):
    return JobsApiExtractor(
        search_term=source_spec.config["search_term"],
        location=source_spec.config["location"],
        results_wanted=source_spec.config.get("results_wanted", 100),
    )


def build_postgres_source_extractor(source_spec, credentials):
    connector = build_destination_connector(
        destination_type="postgres",
        credentials=credentials,
    )
    return PostgresExtractor(
        connector=connector,
        query=source_spec.config["query"],
    )
