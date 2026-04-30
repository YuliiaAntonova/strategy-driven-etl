from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass(frozen=True)
class ConnectionSpec:
    type: str
    credentials: dict[str, Any] = field(default_factory=dict)
    config: dict[str, Any] = field(default_factory=dict)


@dataclass(frozen=True)
class TransformSpec:
    type: str
    config: dict[str, Any] = field(default_factory=dict)


@dataclass(frozen=True)
class LoadBehaviorSpec:
    """Subset of YAML ``load_behavior`` that the pipeline runtime reads.

    Fields: ``profile``, ``primary_key``, ``date_column``, ``hash_column``,
    ``hash_columns``. Additional keys under ``load_behavior`` are ignored unless you
    extend the spec builder.
    """

    profile: str = "historized_snapshot"
    primary_key: str | None = None
    date_column: str = "date_loaded"
    hash_column: str = "row_hash"
    hash_columns: list[str] = field(default_factory=list)


@dataclass(frozen=True)
class PipelineSpec:
    pipeline_name: str
    dataset: str
    source: ConnectionSpec
    destination: ConnectionSpec
    transforms: list[TransformSpec] = field(default_factory=list)
    load_behavior: LoadBehaviorSpec = field(default_factory=LoadBehaviorSpec)
    extract_chunk_size: int | None = None
    write_chunk_size: int | None = None
    environment: str = "runtime"
