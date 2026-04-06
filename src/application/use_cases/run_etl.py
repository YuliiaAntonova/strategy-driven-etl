from __future__ import annotations

from pathlib import Path

from src.application.pipeline.pipeline import Pipeline
from src.application.pipeline.profiles import (
    ALLOWED_WRITERS_BY_LOAD_MODE,
    DEFAULT_WRITE_MODE_BY_LOAD_MODE,
    PIPELINE_PROFILES,
    PipelineProfile,
)
from src.application.pipeline.registry import DETECTOR_FACTORIES, WRITER_FACTORIES
from src.config.settings import settings
from src.domain.contracts.extractor import BaseExtractor
from src.domain.contracts.transformer import BaseTransformer
from src.domain.models.pipeline_context import PipelineContext
from src.infrastructure.connectors.factory import get_postgres_connector
from src.infrastructure.extractors.csv import CSVExtractor
from src.infrastructure.extractors.postgres import PostgresExtractor
from src.infrastructure.transformers.composite import CompositeTransformer
from src.infrastructure.transformers.hash_columns import HashColumnsTransformer
from src.infrastructure.transformers.jobs import JobsAuditTransformer


def _resolve_runtime_profile(
    load_mode: str,
    write_mode: str | None,
    profile_name: str | None,
) -> PipelineProfile:
    if profile_name:
        try:
            return PIPELINE_PROFILES[profile_name]
        except KeyError:
            raise ValueError(f"Unsupported profile: {profile_name}") from None

    resolved_write_mode = write_mode or DEFAULT_WRITE_MODE_BY_LOAD_MODE[load_mode]
    allowed_writers = ALLOWED_WRITERS_BY_LOAD_MODE[load_mode]
    if resolved_write_mode not in allowed_writers:
        allowed = ", ".join(sorted(allowed_writers))
        raise ValueError(f"{load_mode} supports only write-mode(s): {allowed}")

    writer_for_later_batches = "append" if load_mode == "full" else resolved_write_mode
    requires_primary_key = load_mode != "full"
    return PipelineProfile(
        name=f"{load_mode}:{resolved_write_mode}",
        detector_key=load_mode,
        initial_writer_key=resolved_write_mode,
        subsequent_writer_key=writer_for_later_batches,
        requires_primary_key=requires_primary_key,
    )


def run_etl(
    load_mode: str = "full",
    write_mode: str | None = None,
    date_column: str = "date_loaded",
    primary_key: str | None = None,
    hash_column: str = "row_hash",
    extract_chunk_size: int | None = None,
    write_chunk_size: int | None = None,
    extractor: BaseExtractor | None = None,
    transformer: BaseTransformer | None = None,
    profile: str | None = None,
    connector=None,
) -> None:
    runtime_profile = _resolve_runtime_profile(load_mode=load_mode, write_mode=write_mode, profile_name=profile)
    if runtime_profile.requires_primary_key and not primary_key:
        raise ValueError(f"Profile '{runtime_profile.name}' requires --primary-key")

    source_path = Path(settings.source_file)
    if not source_path.exists():
        raise FileNotFoundError(f"Source file does not exist: {source_path}")
    if source_path.stat().st_size == 0:
        raise ValueError(f"Source file is empty: {source_path}")

    context = PipelineContext(
        dataset="jobs",
        dt=PipelineContext.utc_today(),
        run_id=PipelineContext.utc_run_id(),
        environment=settings.environment,
    )

    resolved_connector = get_postgres_connector(connector)

    extractor = extractor or CSVExtractor(file_path=str(source_path))
    transformer = transformer or CompositeTransformer(
        transformers=[
            JobsAuditTransformer(context=context, source_name=settings.source_name),
            HashColumnsTransformer(columns=settings.hash_columns, output_column=hash_column),
        ]
    )

    detector_factory = DETECTOR_FACTORIES[runtime_profile.detector_key]
    change_detector = detector_factory(date_column, primary_key, hash_column)

    def state_reader():
        target_extractor = PostgresExtractor(
            connector=resolved_connector,
            query=f"select * from {settings.target_table}",
        )
        try:
            return target_extractor.extract()
        except Exception:
            empty_source = extractor.extract().iloc[0:0].copy()
            return transformer.transform(empty_source)

    def writer_resolver(batch_index: int):
        writer_key = runtime_profile.initial_writer_key if batch_index == 0 else runtime_profile.subsequent_writer_key
        writer_factory = WRITER_FACTORIES[writer_key]
        return writer_factory(resolved_connector, settings.target_table, primary_key)

    pipeline = Pipeline(
        extractor=extractor,
        transformer=transformer,
        change_detector=change_detector,
        state_reader=state_reader,
        writer_resolver=writer_resolver,
        write_chunk_size=write_chunk_size,
    )
    pipeline.run(extract_chunk_size=extract_chunk_size)
