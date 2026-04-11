"""Run the main ETL pipeline.

This is a thin, CLI-stable facade that validates inputs and wires a Pipeline via
application-level builders.
"""

from __future__ import annotations

from pathlib import Path

from src.application.use_cases.etl.config import RunEtlConfig
from src.application.use_cases.etl.pipeline_builder import EtlOverrides, EtlPipelineBuilder
from src.application.use_cases.etl.profile_resolution import resolve_runtime_profile
from src.application.use_cases.etl.source_validation import ensure_non_empty_file
from src.config.settings import settings
from src.domain.contracts.extractor import BaseExtractor
from src.domain.contracts.transformer import BaseTransformer


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
    target_table: str | None = None,
) -> None:
    """Execute the ETL pipeline according to CLI-configured parameters."""
    source_path = Path(settings.source_file)
    ensure_non_empty_file(source_path)

    config = RunEtlConfig(
        load_mode=load_mode,
        write_mode=write_mode,
        date_column=date_column,
        primary_key=primary_key,
        hash_column=hash_column,
        extract_chunk_size=extract_chunk_size,
        write_chunk_size=write_chunk_size,
        profile=profile,
    )
    runtime_profile = resolve_runtime_profile(config)
    config.ensure_primary_key_if_required(
        requires_primary_key=runtime_profile.requires_primary_key,
        profile_name=runtime_profile.name,
    )

    pipeline = EtlPipelineBuilder(
        runtime_profile=runtime_profile,
        source_path=source_path,
        overrides=EtlOverrides(
            connector=connector,
            extractor=extractor,
            transformer=transformer,
            target_table=target_table,
        ),
    ).build(config)

    pipeline.run(extract_chunk_size=config.extract_chunk_size)
