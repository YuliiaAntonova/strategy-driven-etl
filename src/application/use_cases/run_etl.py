from pathlib import Path

from src.application.services.load_strategy_factory import get_load_strategy
from src.application.services.write_strategy_factory import get_write_strategy
from src.config.settings import settings
from src.domain.models.pipeline_context import PipelineContext
from src.infrastructure.connectors.postgres import PostgreSQLConnector
from src.infrastructure.extractors.csv import CSVExtractor
from src.infrastructure.extractors.postgres import PostgresExtractor
from src.infrastructure.transformers.hash_columns import HashColumnsTransformer
from src.infrastructure.transformers.jobs import JobsAuditTransformer


def run_etl(
    load_mode: str = "full",
    write_mode: str = "replace",
    date_column: str = "date_loaded",
    primary_key: str | None = None,
    hash_column: str = "row_hash",
) -> None:
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

    connector = PostgreSQLConnector(
        host=settings.postgres_host,
        database=settings.postgres_db,
        user=settings.postgres_user,
        password=settings.postgres_password,
        port=settings.postgres_port,
    )

    extractor = CSVExtractor(file_path=str(source_path))
    transformer = JobsAuditTransformer(
        context=context,
        source_name=settings.source_name,
    )

    incoming_df = extractor.extract()
    incoming_df = transformer.transform(incoming_df)

    hash_transformer = HashColumnsTransformer(
        columns=settings.hash_columns,
        output_column=hash_column,
    )
    incoming_df = hash_transformer.transform(incoming_df)

    target_extractor = PostgresExtractor(
        connector=connector,
        query=f"select * from {settings.target_table}",
    )

    try:
        existing_df = target_extractor.extract()
    except Exception:
        existing_df = incoming_df.iloc[0:0].copy()

    load_strategy = get_load_strategy(
        load_mode=load_mode,
        date_column=date_column,
        primary_key=primary_key,
        hash_column=hash_column,
    )

    load_df = load_strategy.prepare(incoming_df=incoming_df, existing_df=existing_df)

    if load_df.empty:
        print("No data to load")
        return

    write_strategy = get_write_strategy(
        write_mode=write_mode,
        connector=connector,
        table_name=settings.target_table,
        primary_key=primary_key,
    )

    write_strategy.write(load_df)