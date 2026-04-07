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
    ai_document_table = os.getenv("AI_DOCUMENT_TABLE", "ai_documents")
    ai_chunk_table = os.getenv("AI_CHUNK_TABLE", "ai_chunks")

    jobs_search_term = os.getenv("JOBS_SEARCH_TERM", "data engineer")
    jobs_location = os.getenv("JOBS_LOCATION", "Berlin")
    jobs_results_wanted = int(os.getenv("JOBS_RESULTS_WANTED", "10"))

    source_name = os.getenv("SOURCE_NAME", "jobs_api")
    environment = os.getenv("ENVIRONMENT", "local")
    hash_columns = _split_csv(os.getenv(
        "HASH_COLUMNS",
        "title,company,location,job_type,description,min_amount,max_amount,currency",
    ))

    ai_default_profile = os.getenv("AI_DEFAULT_PROFILE", "jobs_rag_local")
    ai_chunker = os.getenv("AI_CHUNKER", "recursive")
    ai_embedder = os.getenv("AI_EMBEDDER", "token_frequency")
    ai_retriever = os.getenv("AI_RETRIEVER", "keyword")
    ai_llm_provider = os.getenv("AI_LLM_PROVIDER", "template")
    ai_chunk_size = int(os.getenv("AI_CHUNK_SIZE", "900"))
    ai_chunk_overlap = int(os.getenv("AI_CHUNK_OVERLAP", "120"))
    ai_fetch_k = int(os.getenv("AI_FETCH_K", "20"))
    ai_top_k = int(os.getenv("AI_TOP_K", "5"))
    ai_reranker = os.getenv("AI_RERANKER", "keyword_metadata")
    ai_prompt_builder = os.getenv("AI_PROMPT_BUILDER", "grounded")
    ai_answer_generator = os.getenv("AI_ANSWER_GENERATOR", "template")
    openai_api_key = os.getenv("OPENAI_API_KEY", "")
    openai_model = os.getenv("OPENAI_MODEL", "gpt-4o-mini")

    agent_task_table = os.getenv("AGENT_TASK_TABLE", "agent_tasks")
    agent_task_step_table = os.getenv("AGENT_TASK_STEP_TABLE", "agent_task_steps")
    ai_document_columns = _split_csv(os.getenv(
        "AI_DOCUMENT_COLUMNS",
        "id,title,company,location,job_type,description,skills,date_posted,job_url",
    ))
    ai_metadata_columns = _split_csv(os.getenv(
        "AI_METADATA_COLUMNS",
        "id,title,company,location,job_type,date_posted,job_url,source_name,environment",
    ))


settings = Settings()
