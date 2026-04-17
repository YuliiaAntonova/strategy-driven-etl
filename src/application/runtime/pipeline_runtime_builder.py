from __future__ import annotations

from collections.abc import Callable

from pandas import DataFrame
from sqlalchemy.exc import ProgrammingError

from src.application.pipeline.pipeline import Pipeline
from src.application.pipeline.profiles import PIPELINE_PROFILES
from src.application.pipeline.registry import DETECTOR_FACTORIES, WRITER_FACTORIES
from src.domain.models.pipeline_context import PipelineContext
from src.infrastructure.extractors.postgres import PostgresExtractor


class PipelineRuntimeBuilder:
    def __init__(
        self,
        *,
        source_registry,
        destination_registry,
        transform_registry,
        secret_resolver,
    ):
        self.source_registry = source_registry
        self.destination_registry = destination_registry
        self.transform_registry = transform_registry
        self.secret_resolver = secret_resolver

    def build(self, spec) -> Pipeline:
        runtime_profile = PIPELINE_PROFILES[spec.load_behavior.profile]
        if runtime_profile.requires_primary_key and not spec.load_behavior.primary_key:
            raise ValueError(
                f"Profile '{runtime_profile.name}' requires primary_key"
            )

        context = PipelineContext(
            dataset=spec.dataset,
            dt=PipelineContext.utc_today(),
            run_id=PipelineContext.utc_run_id(),
            environment=spec.environment,
        )

        source_creds = self.secret_resolver.resolve(spec.source.credentials)
        dest_creds = self.secret_resolver.resolve(spec.destination.credentials)

        extractor = self.source_registry.build(spec.source, source_creds)
        connector = self.destination_registry.build(spec.destination, dest_creds)
        transformer = self.transform_registry.build_chain(spec.transforms, context)

        detector_factory = DETECTOR_FACTORIES[runtime_profile.detector_key]
        change_detector = detector_factory(
            spec.load_behavior.date_column,
            spec.load_behavior.primary_key,
            spec.load_behavior.hash_column,
        )

        state_reader = self._build_state_reader(
            connector=connector,
            extractor=extractor,
            transformer=transformer,
            target_table=spec.destination.config["table"],
        )
        writer_resolver = self._build_writer_resolver(
            connector=connector,
            target_table=spec.destination.config["table"],
            primary_key=spec.load_behavior.primary_key,
            runtime_profile=runtime_profile,
        )

        return Pipeline(
            extractor=extractor,
            transformer=transformer,
            change_detector=change_detector,
            state_reader=state_reader,
            writer_resolver=writer_resolver,
            write_chunk_size=spec.write_chunk_size,
        )

    def _build_state_reader(
        self,
        *,
        connector,
        extractor,
        transformer,
        target_table: str,
    ) -> Callable[[], DataFrame]:
        def _state_reader() -> DataFrame:
            target_extractor = PostgresExtractor(
                connector=connector,
                query=f"select * from {target_table}",
            )
            try:
                return target_extractor.extract()
            except ProgrammingError:
                empty_source = extractor.extract().iloc[0:0].copy()
                return transformer.transform(empty_source)

        return _state_reader

    def _build_writer_resolver(self, *, connector, target_table: str, primary_key: str | None, runtime_profile):
        def _writer_resolver(batch_index: int):
            writer_key = (
                runtime_profile.initial_writer_key
                if batch_index == 0
                else runtime_profile.subsequent_writer_key
            )
            writer_factory = WRITER_FACTORIES[writer_key]
            return writer_factory(connector, target_table, primary_key)

        return _writer_resolver
