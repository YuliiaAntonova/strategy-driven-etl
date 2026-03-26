from pathlib import Path

from src.application.services.load_strategy_factory import get_load_strategy
from src.application.services.write_strategy_factory import get_write_strategy
from src.config.settings import settings
from src.domain.contracts.extractor import BaseExtractor
from src.domain.contracts.transformer import BaseTransformer
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
    extract_chunk_size: int | None = None,
    write_chunk_size: int | None = None,
    extractor: BaseExtractor | None = None,
    transformer: BaseTransformer | None = None,
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

    extractor = extractor or CSVExtractor(file_path=str(source_path))
    transformer = transformer or JobsAuditTransformer(
        context=context,
        source_name=settings.source_name,
    )

    load_strategy = get_load_strategy(
        load_mode=load_mode,
        date_column=date_column,
        primary_key=primary_key,
        hash_column=hash_column,
    )

    target_extractor = PostgresExtractor(
        connector=connector,
        query=f"select * from {settings.target_table}",
    )
    try:
        existing_df = target_extractor.extract()
    except Exception:
        existing_df = None

    def _process_batch(batch_df, is_first_batch: bool) -> bool:
        nonlocal existing_df

        batch_df = transformer.transform(batch_df)

        hash_transformer = HashColumnsTransformer(
            columns=settings.hash_columns,
            output_column=hash_column,
        )
        batch_df = hash_transformer.transform(batch_df)

        current_existing_df = (
            batch_df.iloc[0:0].copy()
            if existing_df is None
            else existing_df
        )

        load_df = load_strategy.prepare(
            incoming_df=batch_df,
            existing_df=current_existing_df,
        )

        if load_df.empty:
            return False

        effective_write_mode = write_mode
        if write_mode == "replace" and extract_chunk_size:
            effective_write_mode = "replace" if is_first_batch else "append"

        write_strategy = get_write_strategy(
            write_mode=effective_write_mode,
            connector=connector,
            table_name=settings.target_table,
            primary_key=primary_key,
        )
        write_strategy.write(load_df, chunk_size=write_chunk_size)
        return True

    if extract_chunk_size:
        first_chunk = True

        for chunk_df in extractor.extract_in_chunks(extract_chunk_size):
            wrote_rows = _process_batch(chunk_df, is_first_batch=first_chunk)
            if wrote_rows and first_chunk:
                first_chunk = False
        return

    incoming_df = extractor.extract()
    wrote_rows = _process_batch(incoming_df, is_first_batch=True)
    if not wrote_rows:
        print("No data to load")