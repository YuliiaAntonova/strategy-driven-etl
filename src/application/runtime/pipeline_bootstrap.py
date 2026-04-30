from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass(frozen=True, kw_only=True)
class PipelineBootstrapConfig:
    """Keyword arguments accepted by ``pipeline()`` / ``UserPipeline`` before YAML merge."""

    pipeline_name: str
    source_profile: str | None = None
    destination_profile: str | None = None
    options_profile: str | None = None
    config_dir: str = "config"
    destination: str | None = None
    dataset_name: str | None = None
    credentials: dict[str, Any] | None = None
    profile: str = "historized_snapshot"
    primary_key: str | None = None
    date_column: str = "date_loaded"
    hash_column: str = "row_hash"
    hash_columns: list[str] | None = None
    extract_chunk_size: int | None = None
    write_chunk_size: int | None = None
    environment: str = "runtime"
    destination_config: dict[str, Any] | None = None


@dataclass(frozen=True)
class PipelineDefaults:
    profile: str = "historized_snapshot"
    primary_key: str | None = None
    date_column: str = "date_loaded"
    hash_column: str = "row_hash"
    hash_columns: list[str] = field(default_factory=list)
    extract_chunk_size: int | None = None
    write_chunk_size: int | None = None
    environment: str = "runtime"
