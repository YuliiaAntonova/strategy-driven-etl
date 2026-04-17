from src import pipeline, source, resource
from src.infrastructure.extractors.jobs_api import JobsApiExtractor

@resource(
    name="jobs",
    table_name="jobs",
    primary_key="id",
    columns=["title", "company", "location", "description", "job_type"],
)
def jobs_resource(search_term: str, location: str, results_wanted: int = 100):
    extractor = JobsApiExtractor(
        search_term=search_term,
        location=location,
        results_wanted=results_wanted,
    )
    df = extractor.extract()

    for row in df.to_dict(orient="records"):
        yield row

@source(name="jobs_source")
def jobs_source(search_term: str, location: str, results_wanted: int = 100):
    return [
        jobs_resource(
            search_term=search_term,
            location=location,
            results_wanted=results_wanted,
        )
    ]

p = pipeline(
    pipeline_name="jobs_pipeline",
    destination="postgres",
    dataset_name="jobs",
    credentials={
        "host": "localhost",
        "port": 5432,
        "database": "world",
        "user": "postgres",
        "password": "postgres",
    },
    profile="historized_snapshot",
    primary_key="id",
    hash_columns=["title", "company", "location", "description", "job_type"],
    extract_chunk_size=1000,
    write_chunk_size=500,
)

p.run(
    jobs_source(
        search_term="data engineer",
        location="Berlin",
        results_wanted=100,
    )
)