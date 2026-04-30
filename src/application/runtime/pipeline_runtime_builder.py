from __future__ import annotations

from collections.abc import Callable

from pandas import DataFrame
from sqlalchemy.exc import ProgrammingError, SQLAlchemyError

from src.application.pipeline.pipeline import Pipeline
from src.application.pipeline.profiles import PIPELINE_PROFILES
from src.application.pipeline.registry import DETECTOR_FACTORIES, WRITER_FACTORIES
from src.domain.models.pipeline_context import PipelineContext
from src.infrastructure.extractors.full_table_sql import select_star_from_single_table
from src.infrastructure.extractors.sql import SQLExtractor


class PipelineRuntimeBuilder:
    def __init__(
        self,
        *,
        connector_registry,
        transform_registry,
        secret_resolver,
    ):
        self.connector_registry = connector_registry
        self.transform_registry = transform_registry
        self.secret_resolver = secret_resolver

    def build(self, spec) -> Pipeline:
        runtime_profile = PIPELINE_PROFILES[spec.load_behavior.profile]

        if runtime_profile.requires_primary_key and not spec.load_behavior.primary_key:
            raise ValueError(f"Profile '{runtime_profile.name}' requires primary_key")

        context = PipelineContext(
            dataset=spec.dataset,
            dt=PipelineContext.utc_today(),
            run_id=PipelineContext.utc_run_id(),
            environment=spec.environment,
        )

        source_creds = self.secret_resolver.resolve(spec.source.credentials)
        dest_creds = self.secret_resolver.resolve(spec.destination.credentials)

        extractor = self.connector_registry.build_extractor(spec.source, source_creds)
        connector = self.connector_registry.build_loader(spec.destination, dest_creds)
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
            destination_type=spec.destination.type,
        )

        writer_resolver = self._build_writer_resolver(
            connector=connector,
            target_table=spec.destination.config["table"],
            primary_key=spec.load_behavior.primary_key,
            runtime_profile=runtime_profile,
            destination_type=spec.destination.type,
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
        destination_type: str,
    ) -> Callable[[], DataFrame]:
        def _state_reader() -> DataFrame:
            target_extractor = SQLExtractor(
                connector=connector,
                query=select_star_from_single_table(
                    destination_type=destination_type,
                    table_name=target_table,
                ),
            )

            try:
                return target_extractor.extract()
            except (ProgrammingError, SQLAlchemyError):
                empty_source = extractor.extract().iloc[0:0].copy()
                return transformer.transform(empty_source)

        return _state_reader

    def _build_writer_resolver(
        self,
        *,
        connector,
        target_table: str,
        primary_key: str | None,
        runtime_profile,
        destination_type: str,
    ):
        def _writer_resolver(batch_index: int):
            writer_key = (
                runtime_profile.initial_writer_key
                if batch_index == 0
                else runtime_profile.subsequent_writer_key
            )

            writer_factory = WRITER_FACTORIES[writer_key]

            return writer_factory(
                connector,
                target_table,
                primary_key,
                destination_type,
            )

        return _writer_resolver