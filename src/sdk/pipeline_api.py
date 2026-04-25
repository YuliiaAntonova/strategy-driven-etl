from __future__ import annotations

from collections.abc import Iterable
from dataclasses import dataclass, field
from typing import Any

import pandas as pd
from pandas import DataFrame

from src.application.runtime.destination_registry import DestinationRegistry
from src.application.runtime.pipeline_runtime_builder import PipelineRuntimeBuilder
from src.application.runtime.profile_loader import ProfileLoader
from src.application.runtime.secret_resolver import SecretResolver
from src.application.runtime.source_registry import SourceRegistry
from src.application.runtime.transform_registry import TransformRegistry
from src.application.specs.pipeline_spec import ConnectionSpec, LoadBehaviorSpec, PipelineSpec, TransformSpec
from src.infrastructure.connectors.catalog import DESTINATION_FACTORIES
from src.infrastructure.extractors.catalog import SOURCE_FACTORIES
from src.infrastructure.transformers.catalog import TRANSFORM_FACTORIES
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
        source_profile: str | None = None,
        destination_profile: str | None = None,
        options_profile: str | None = None,
        config_dir: str = "config",
        destination: str | None = None,
        dataset_name: str | None = None,
        credentials: dict[str, Any] | None = None,
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
        self.profile_loader = ProfileLoader(config_dir=config_dir)
        self.source_profile = source_profile
        self.destination_profile = destination_profile
        self.options_profile = options_profile

        self.source_config = self.profile_loader.load_source(source_profile) if source_profile else None
        self.destination_profile_config = self.profile_loader.load_destination(destination_profile) if destination_profile else None
        self.options_config = self.profile_loader.load_options(options_profile) if options_profile else None

        destination_from_profile = self.destination_profile_config or {}
        options = self.options_config or {}
        load_behavior = options.get("load_behavior", {})
        runtime = options.get("runtime", {})

        self.destination = destination or destination_from_profile.get("type")
        if not self.destination:
            raise ValueError("destination or destination_profile is required")

        self.dataset_name = dataset_name or options.get("dataset_name") or options.get("table_name")
        if not self.dataset_name:
            raise ValueError("dataset_name or options.dataset_name/table_name is required")

        self.credentials = credentials or destination_from_profile.get("credentials", {})
        self.destination_config = {**destination_from_profile.get("config", {}), **dict(destination_config or {})}

        self.defaults = PipelineDefaults(
            profile=load_behavior.get("profile", profile),
            primary_key=load_behavior.get("primary_key", primary_key),
            date_column=load_behavior.get("date_column", date_column),
            hash_column=load_behavior.get("hash_column", hash_column),
            hash_columns=list(load_behavior.get("hash_columns", hash_columns or [])),
            extract_chunk_size=runtime.get("extract_chunk_size", extract_chunk_size),
            write_chunk_size=runtime.get("write_chunk_size", write_chunk_size),
            environment=runtime.get("environment", environment),
        )
        self.runtime_builder = self._build_runtime_builder()

    def run(self, data=None, table_name: str | None = None) -> None:
        if data is None:
            self._run_profile_source(table_name=table_name)
            return
        if isinstance(data, SourceInvocation):
            for resource in data.resources():
                self._run_resource(resource, source_name=data.name)
            return
        if isinstance(data, ResourceInvocation):
            self._run_resource(data)
            return
        self._run_raw_data(data=data, table_name=table_name)

    def _run_profile_source(self, table_name: str | None = None) -> None:
        if not self.source_config:
            raise ValueError("run() without data requires source_profile")
        source_spec = ConnectionSpec(
            type=self.source_config["type"],
            config=dict(self.source_config.get("config", {})),
            credentials=dict(self.source_config.get("credentials", {})),
        )
        resource_name = self.source_config.get("resource_name") or self.source_profile or source_spec.type
        target_table = table_name or self._option("table_name") or resource_name
        transforms = self._configured_transforms(source_name=resource_name)
        spec = self._build_pipeline_spec(
            source_spec=source_spec,
            table_name=target_table,
            primary_key=self.defaults.primary_key,
            transforms=transforms,
        )
        self._build_and_run(spec)

    def _run_raw_data(self, data, table_name: str | None = None) -> None:
        source_spec = ConnectionSpec(type="memory", config={"records": self._normalize_records(data)})
        resource_table = table_name or self._option("table_name") or self.dataset_name
        spec = self._build_pipeline_spec(
            source_spec=source_spec,
            table_name=resource_table,
            primary_key=self.defaults.primary_key,
            transforms=self._configured_transforms(source_name="memory"),
        )
        self._build_and_run(spec)

    def _run_resource(self, resource: ResourceInvocation, source_name: str | None = None) -> None:
        records = resource.records()
        source_spec = ConnectionSpec(type="memory", config={"records": records})
        effective_primary_key = resource.primary_key or self.defaults.primary_key
        effective_source_name = resource.source_name or source_name or resource.name
        table_name = self._option("table_name") or resource.table_name
        transforms = self._configured_transforms(source_name=effective_source_name)
        spec = self._build_pipeline_spec(
            source_spec=source_spec,
            table_name=table_name,
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
            destination=ConnectionSpec(type=self.destination, credentials=self.credentials, config=destination_config),
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

    def _configured_transforms(self, *, source_name: str) -> list[TransformSpec]:
        configured = self._option("transforms")
        if configured:
            transforms: list[TransformSpec] = []
            for transform in configured:
                transform_type = transform["type"]
                transform_config = dict(transform.get("config", {}))
                if transform_type == "jobs_audit":
                    transform_config.setdefault("source_name", source_name)
                if transform_type == "hash_columns":
                    transform_config.setdefault("columns", self.defaults.hash_columns)
                    transform_config.setdefault("output_column", self.defaults.hash_column)
                transforms.append(TransformSpec(type=transform_type, config=transform_config))
            return transforms
        return self._default_transforms(source_name=source_name, hash_columns=self.defaults.hash_columns)

    def _default_transforms(self, *, source_name: str, hash_columns: list[str]) -> list[TransformSpec]:
        transforms = [TransformSpec(type="jobs_audit", config={"source_name": source_name})]
        if self.defaults.profile == "historized_snapshot" and not hash_columns:
            raise ValueError("historized_snapshot requires hash_columns so the versioned writer can compare row_hash")
        if hash_columns:
            transforms.append(TransformSpec(type="hash_columns", config={"columns": hash_columns, "output_column": self.defaults.hash_column}))
        return transforms

    def _build_and_run(self, spec: PipelineSpec) -> None:
        runtime_pipeline = self.runtime_builder.build(spec)
        runtime_pipeline.run(extract_chunk_size=spec.extract_chunk_size)

    def _build_runtime_builder(self) -> PipelineRuntimeBuilder:
        source_registry = SourceRegistry()
        for source_type, factory in SOURCE_FACTORIES.items():
            source_registry.register(source_type, factory)
        destination_registry = DestinationRegistry()
        for destination_type, factory in DESTINATION_FACTORIES.items():
            destination_registry.register(destination_type, factory)
        transform_registry = TransformRegistry()
        for transform_type, factory in TRANSFORM_FACTORIES.items():
            transform_registry.register(transform_type, factory)
        return PipelineRuntimeBuilder(
            source_registry=source_registry,
            destination_registry=destination_registry,
            transform_registry=transform_registry,
            secret_resolver=SecretResolver(),
        )

    def _option(self, key: str, default: Any = None) -> Any:
        if not self.options_config:
            return default
        return self.options_config.get(key, default)

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
    source_profile: str | None = None,
    destination_profile: str | None = None,
    options_profile: str | None = None,
    config_dir: str = "config",
    destination: str | None = None,
    dataset_name: str | None = None,
    credentials: dict[str, Any] | None = None,
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
        source_profile=source_profile,
        destination_profile=destination_profile,
        options_profile=options_profile,
        config_dir=config_dir,
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
