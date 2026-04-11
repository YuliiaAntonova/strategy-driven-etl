"""Pipeline wiring for the ETL use case."""

from __future__ import annotations

from collections.abc import Callable
from pathlib import Path

from pandas import DataFrame
from sqlalchemy.exc import ProgrammingError

from src.application.pipeline.pipeline import Pipeline
from src.application.pipeline.registry import DETECTOR_FACTORIES, WRITER_FACTORIES
from src.application.pipeline.profiles import PipelineProfile
from src.application.use_cases.etl.config import RunEtlConfig
from src.domain.contracts.extractor import BaseExtractor
from src.domain.contracts.transformer import BaseTransformer
from src.domain.models.pipeline_context import PipelineContext
from src.infrastructure.connectors.factory import get_postgres_connector
from src.infrastructure.extractors.csv import CSVExtractor
from src.infrastructure.extractors.postgres import PostgresExtractor
from src.infrastructure.transformers.composite import CompositeTransformer
from src.infrastructure.transformers.hash_columns import HashColumnsTransformer
from src.infrastructure.transformers.jobs import JobsAuditTransformer


class EtlOverrides:
    """Optional injected dependencies for testing/advanced wiring."""

    def __init__(
        self,
        *,
        connector=None,
        extractor: BaseExtractor | None = None,
        transformer: BaseTransformer | None = None,
        target_table: str | None = None,
    ):
        self.connector = connector
        self.extractor = extractor
        self.transformer = transformer
        self.target_table = target_table


class EtlPipelineBuilder:
    """Builds a configured `Pipeline` instance for the ETL use case."""

    def __init__(
        self,
        *,
        runtime_profile: PipelineProfile,
        source_path: Path,
        overrides: EtlOverrides | None = None,
    ):
        self._runtime_profile = runtime_profile
        self._source_path = source_path
        self._overrides = overrides or EtlOverrides()

    def build(self, config: RunEtlConfig) -> Pipeline:
        context = PipelineContext(
            dataset="jobs",
            dt=PipelineContext.utc_today(),
            run_id=PipelineContext.utc_run_id(),
            environment=settings.environment,
        )

        resolved_connector = get_postgres_connector(self._overrides.connector)

        extractor = self._overrides.extractor or CSVExtractor(file_path=str(self._source_path))
        transformer = self._overrides.transformer or CompositeTransformer(
            transformers=[
                JobsAuditTransformer(context=context, source_name=settings.source_name),
                HashColumnsTransformer(columns=settings.hash_columns, output_column=config.hash_column),
            ]
        )

        detector_factory = DETECTOR_FACTORIES[self._runtime_profile.detector_key]
        change_detector = detector_factory(config.date_column, config.primary_key, config.hash_column)

        state_reader = self._build_state_reader(
            resolved_connector=resolved_connector,
            extractor=extractor,
            transformer=transformer,
        )
        writer_resolver = self._build_writer_resolver(
            resolved_connector=resolved_connector,
            primary_key=config.primary_key,
        )

        return Pipeline(
            extractor=extractor,
            transformer=transformer,
            change_detector=change_detector,
            state_reader=state_reader,
            writer_resolver=writer_resolver,
            write_chunk_size=config.write_chunk_size,
        )

    def _build_state_reader(
        self,
        *,
        resolved_connector,
        extractor: BaseExtractor,
        transformer: BaseTransformer,
    ) -> Callable[[], DataFrame]:
        def _state_reader() -> DataFrame:
            target_extractor = PostgresExtractor(
                connector=resolved_connector,
                query=f"select * from {self._overrides.target_table or settings.target_table}",
            )
            try:
                return target_extractor.extract()
            except ProgrammingError:
                # Fallback: treat missing target as empty but keep correct schema.
                empty_source = extractor.extract().iloc[0:0].copy()
                return transformer.transform(empty_source)

        return _state_reader

    def _build_writer_resolver(self, *, resolved_connector, primary_key: str | None):
        def _writer_resolver(batch_index: int):
            writer_key = (
                self._runtime_profile.initial_writer_key
                if batch_index == 0
                else self._runtime_profile.subsequent_writer_key
            )
            writer_factory = WRITER_FACTORIES[writer_key]
            return writer_factory(resolved_connector, self._overrides.target_table or settings.target_table, primary_key)

        return _writer_resolver


# Local import to avoid circular deps (settings imports config, etc.)
from src.config.settings import settings  # noqa: E402  pylint: disable=wrong-import-position




