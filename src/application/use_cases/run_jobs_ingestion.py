from src.application.use_cases.run_pipeline import run_pipeline
from src.config.settings import settings
from src.domain.models.pipeline_context import PipelineContext
from src.infrastructure.extractors.jobs_api import JobsApiExtractor
from src.infrastructure.loaders.csv import CSVLoader
from src.infrastructure.transformers.jobs import JobsAuditTransformer


def run_jobs_ingestion(
    dataset: str = "jobs",
    dt: str | None = None,
    run_id: str | None = None,
) -> str:
    if dataset != "jobs":
        raise ValueError("For now only dataset='jobs' is implemented")

    context = PipelineContext(
        dataset=dataset,
        dt=dt or PipelineContext.utc_today(),
        run_id=run_id or PipelineContext.utc_run_id(),
        environment=settings.environment,
    )

    extractor = JobsApiExtractor(
        search_term=settings.jobs_search_term,
        location=settings.jobs_location,
        results_wanted=settings.jobs_results_wanted,
    )
    transformer = JobsAuditTransformer(
        context=context,
        source_name=settings.source_name,
    )
    loader = CSVLoader(file_path=settings.source_file)

    run_pipeline(
        extractor=extractor,
        transformer=transformer,
        loader=loader,
    )
    return settings.source_file
