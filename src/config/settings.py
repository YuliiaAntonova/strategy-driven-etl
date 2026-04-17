"""Application configuration.

Settings are loaded from environment variables (optionally via a .env file).
"""

import os
from dotenv import load_dotenv

load_dotenv()


def _split_csv(value: str) -> list[str]:
    return [item.strip() for item in value.split(',') if item.strip()]


class Settings:
    """Container for application settings loaded from environment variables."""

    source_file = os.getenv("SOURCE_FILE", "data/jobs.csv")

    postgres_host = os.getenv("POSTGRES_HOST", "localhost")
    postgres_db = os.getenv("POSTGRES_DB", "world")
    postgres_user = os.getenv("POSTGRES_USER", "postgres")
    postgres_password = os.getenv("POSTGRES_PASSWORD", "postgres")
    postgres_port = int(os.getenv("POSTGRES_PORT", "5432"))

    target_table = os.getenv("TARGET_TABLE", "jobs")

    jobs_search_term = os.getenv("JOBS_SEARCH_TERM", "data engineer")
    jobs_location = os.getenv("JOBS_LOCATION", "Berlin")
    jobs_results_wanted = int(os.getenv("JOBS_RESULTS_WANTED", "10"))

    source_name = os.getenv("SOURCE_NAME", "jobs_api")
    environment = os.getenv("ENVIRONMENT", "local")
    hash_columns = _split_csv(os.getenv(
        "HASH_COLUMNS",
        "title,company,location,job_type,description,min_amount,max_amount,currency",
    ))



settings = Settings()
