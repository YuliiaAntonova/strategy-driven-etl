from __future__ import annotations

from collections.abc import Iterable
from dataclasses import dataclass, field
from typing import Any

import pandas as pd
from pandas import DataFrame

from src.application.runtime.destination_registry import DestinationRegistry
from src.application.runtime.pipeline_runtime_builder import PipelineRuntimeBuilder
from src.application.runtime.secret_resolver import SecretResolver
from src.application.runtime.source_registry import SourceRegistry
from src.application.runtime.transform_registry import TransformRegistry
from src.application.specs.pipeline_spec import (
    ConnectionSpec,
    LoadBehaviorSpec,
    PipelineSpec,
    TransformSpec,
)
from src.infrastructure.connectors.factory import build_destination_connector
from src.infrastructure.extractors.factories import (
    build_csv_extractor,
    build_jobs_api_extractor,
    build_memory_extractor,
    build_postgres_source_extractor,
)
from src.infrastructure.transformers.factories import (
    build_hash_columns_transformer,
    build_identity_transformer,
    build_jobs_audit_transformer,
)
from src.sdk.decorators import ResourceInvocation, SourceInvocation


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


class UserPipeline:
    def __init__(
        self,
        *,
        pipeline_name: str,
        destination: str,
        dataset_name: str,
        credentials: dict[str, Any],
        profile: str = "historized_snapshot",
        primary_key: str | None = None,
        date_column: str = "date_loaded",
        hash_column: str = "row_hash",
        hash_columns: list[str] | None = None,
        extract_chunk_size: int | None = None,
        write_chunk_size: int | None = None,
        environment: str = "runtime",
        destination_config: dict[str, Any] | None = None,
    ):
        self.pipeline_name = pipeline_name
        self.destination = destination
        self.dataset_name = dataset_name
        self.credentials = credentials
        self.destination_config = dict(destination_config or {})
        self.defaults = PipelineDefaults(
            profile=profile,
            primary_key=primary_key,
            date_column=date_column,
            hash_column=hash_column,
            hash_columns=list(hash_columns or []),
            extract_chunk_size=extract_chunk_size,
            write_chunk_size=write_chunk_size,
            environment=environment,
        )
        self.runtime_builder = self._build_runtime_builder()

    def run(self, data, table_name: str | None = None) -> None:
        if isinstance(data, SourceInvocation):
            for resource in data.resources():
                self._run_resource(resource, source_name=data.name)
            return
        if isinstance(data, ResourceInvocation):
            self._run_resource(data)
            return
        self._run_raw_data(data=data, table_name=table_name)

    def _run_raw_data(self, data, table_name: str | None = None) -> None:
        source_spec = ConnectionSpec(
            type="memory",
            config={"records": self._normalize_records(data)},
        )
        resource_table = table_name or self.dataset_name
        spec = self._build_pipeline_spec(
            source_spec=source_spec,
            table_name=resource_table,
            primary_key=self.defaults.primary_key,
            transforms=self._default_transforms(source_name="memory", hash_columns=self.defaults.hash_columns),
        )
        self._build_and_run(spec)

    def _run_resource(self, resource: ResourceInvocation, source_name: str | None = None) -> None:
        records = resource.records()
        source_spec = ConnectionSpec(
            type="memory",
            config={"records": records},
        )
        effective_primary_key = resource.primary_key or self.defaults.primary_key
        effective_source_name = resource.source_name or source_name or resource.name
        hash_columns = resource.columns or self.defaults.hash_columns
        transforms = self._default_transforms(
            source_name=effective_source_name,
            hash_columns=hash_columns,
        )
        spec = self._build_pipeline_spec(
            source_spec=source_spec,
            table_name=resource.table_name,
            primary_key=effective_primary_key,
            transforms=transforms,
        )
        self._build_and_run(spec)

    def _build_pipeline_spec(self, *, source_spec: ConnectionSpec, table_name: str, primary_key: str | None, transforms: list[TransformSpec]) -> PipelineSpec:
        destination_config = {"table": table_name, **self.destination_config}
        return PipelineSpec(
            pipeline_name=self.pipeline_name,
            dataset=self.dataset_name,
            source=source_spec,
            destination=ConnectionSpec(
                type=self.destination,
                credentials=self.credentials,
                config=destination_config,
            ),
            transforms=transforms,
            load_behavior=LoadBehaviorSpec(
                profile=self.defaults.profile,
                primary_key=primary_key,
                date_column=self.defaults.date_column,
                hash_column=self.defaults.hash_column,
                hash_columns=self.defaults.hash_columns,
            ),
            extract_chunk_size=self.defaults.extract_chunk_size,
            write_chunk_size=self.defaults.write_chunk_size,
            environment=self.defaults.environment,
        )

    def _default_transforms(self, *, source_name: str, hash_columns: list[str]) -> list[TransformSpec]:
        transforms = [
            TransformSpec(type="jobs_audit", config={"source_name": source_name})
        ]
        if self.defaults.profile == "historized_snapshot" and not hash_columns:
            raise ValueError(
                "historized_snapshot requires hash_columns so the versioned writer can compare row_hash"
            )
        if hash_columns:
            transforms.append(
                TransformSpec(
                    type="hash_columns",
                    config={
                        "columns": hash_columns,
                        "output_column": self.defaults.hash_column,
                    },
                )
            )
        return transforms

    def _build_and_run(self, spec: PipelineSpec) -> None:
        runtime_pipeline = self.runtime_builder.build(spec)
        runtime_pipeline.run(extract_chunk_size=spec.extract_chunk_size)

    def _build_runtime_builder(self) -> PipelineRuntimeBuilder:
        source_registry = SourceRegistry()
        source_registry.register("memory", build_memory_extractor)
        source_registry.register("csv", build_csv_extractor)
        source_registry.register("jobs_api", build_jobs_api_extractor)
        source_registry.register("postgres", build_postgres_source_extractor)

        destination_registry = DestinationRegistry()
        destination_registry.register(
            "postgres",
            lambda destination_spec, credentials: build_destination_connector(
                destination_type=destination_spec.type,
                credentials=credentials,
            ),
        )

        transform_registry = TransformRegistry()
        transform_registry.register("identity", build_identity_transformer)
        transform_registry.register("jobs_audit", build_jobs_audit_transformer)
        transform_registry.register("hash_columns", build_hash_columns_transformer)

        return PipelineRuntimeBuilder(
            source_registry=source_registry,
            destination_registry=destination_registry,
            transform_registry=transform_registry,
            secret_resolver=SecretResolver(),
        )

    @staticmethod
    def _normalize_records(data) -> Iterable[dict]:
        if isinstance(data, DataFrame):
            return data.to_dict(orient="records")
        if isinstance(data, list):
            return data
        if isinstance(data, dict):
            return [data]
        if isinstance(data, pd.Series):
            return [data.to_dict()]
        if isinstance(data, Iterable):
            return data
        raise TypeError(f"Unsupported run() payload type: {type(data)!r}")



def pipeline(
    *,
    pipeline_name: str,
    destination: str,
    dataset_name: str,
    credentials: dict[str, Any],
    profile: str = "historized_snapshot",
    primary_key: str | None = None,
    date_column: str = "date_loaded",
    hash_column: str = "row_hash",
    hash_columns: list[str] | None = None,
    extract_chunk_size: int | None = None,
    write_chunk_size: int | None = None,
    environment: str = "runtime",
    destination_config: dict[str, Any] | None = None,
) -> UserPipeline:
    return UserPipeline(
        pipeline_name=pipeline_name,
        destination=destination,
        dataset_name=dataset_name,
        credentials=credentials,
        profile=profile,
        primary_key=primary_key,
        date_column=date_column,
        hash_column=hash_column,
        hash_columns=hash_columns,
        extract_chunk_size=extract_chunk_size,
        write_chunk_size=write_chunk_size,
        environment=environment,
        destination_config=destination_config,
    )
