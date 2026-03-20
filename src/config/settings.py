import os
from dotenv import load_dotenv

load_dotenv()


class Settings:
    source_file = os.getenv("SOURCE_FILE", "data/jobs.csv")

    postgres_host = os.getenv("POSTGRES_HOST", "localhost")
    postgres_db = os.getenv("POSTGRES_DB", "world")
    postgres_user = os.getenv("POSTGRES_USER", "postgres")
    postgres_password = os.getenv("POSTGRES_PASSWORD", "postgres")
    postgres_port = int(os.getenv("POSTGRES_PORT", "5432"))

    target_table = os.getenv("TARGET_TABLE", "jobs")

    jobs_search_term = os.getenv("JOBS_SEARCH_TERM", "data engineer")
    jobs_location = os.getenv("JOBS_LOCATION", "Berlin")
    jobs_results_wanted = int(os.getenv("JOBS_RESULTS_WANTED", "100"))

    source_name = os.getenv("SOURCE_NAME", "jobs_api")
    environment = os.getenv("ENVIRONMENT", "local")
    hash_columns = [col.strip() for col in os.getenv("HASH_COLUMNS", "title,company,location").split(",") if col.strip()]


settings = Settings()