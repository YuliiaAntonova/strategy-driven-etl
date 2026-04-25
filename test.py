from src import pipeline


p = pipeline(
    pipeline_name="jobs_pipeline",
    source_profile="jobs_api_berlin",
    destination_profile="local_postgres",
    options_profile="jobs_load",
)

p.run()