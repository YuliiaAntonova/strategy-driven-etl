from __future__ import annotations

from src.infrastructure.extractors.factories import (
    build_csv_extractor,
    build_jobs_api_extractor,
    build_memory_extractor,
    build_postgres_source_extractor,
)

# Strategy/Factory catalog. To add a new source, implement a factory and
# register it here, or later replace this module with entry-point discovery.
SOURCE_FACTORIES = {
    "memory": build_memory_extractor,
    "csv": build_csv_extractor,
    "file": build_csv_extractor,  # file.format=csv / config.file_path for current MVP
    "jobs_api": build_jobs_api_extractor,
    "postgres": build_postgres_source_extractor,
}
