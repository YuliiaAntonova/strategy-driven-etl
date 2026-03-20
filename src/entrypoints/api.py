from src.application.use_cases.run_jobs_ingestion import run_jobs_ingestion


def trigger_jobs_ingestion(dataset: str = "jobs", dt: str | None = None, run_id: str | None = None) -> dict:
    output_file = run_jobs_ingestion(dataset=dataset, dt=dt, run_id=run_id)
    return {
        "status": "ok",
        "dataset": dataset,
        "output_file": output_file,
    }
