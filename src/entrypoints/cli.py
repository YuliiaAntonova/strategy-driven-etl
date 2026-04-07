"""Command line interface entrypoint for local development and ops."""

import argparse

from src.application.ai.profiles import AI_PROFILES
from src.application.pipeline.profiles import PIPELINE_PROFILES, DEFAULT_WRITE_MODE_BY_LOAD_MODE
from src.application.use_cases.answer_query import answer_query
from src.application.use_cases.ask_ai import ask_ai
from src.application.use_cases.run_ai_indexing import run_ai_indexing
from src.application.use_cases.run_etl import run_etl
from src.application.use_cases.run_jobs_ingestion import run_jobs_ingestion


LOAD_MODES = tuple(DEFAULT_WRITE_MODE_BY_LOAD_MODE.keys())
PROFILE_NAMES = tuple(PIPELINE_PROFILES.keys())
WRITE_MODES = tuple(sorted(set(DEFAULT_WRITE_MODE_BY_LOAD_MODE.values())))
AI_PROFILE_NAMES = tuple(AI_PROFILES.keys())


def main():
    """Parse CLI arguments and dispatch to the selected use case."""
    parser = argparse.ArgumentParser()
    subparsers = parser.add_subparsers(dest="command", required=True)

    etl_parser = subparsers.add_parser("run-etl")
    etl_parser.add_argument("--profile", choices=PROFILE_NAMES, default=None)
    etl_parser.add_argument("--load-mode", choices=LOAD_MODES, default="full")
    etl_parser.add_argument("--write-mode", choices=WRITE_MODES, default=None)
    etl_parser.add_argument("--date-column", default="date_loaded")
    etl_parser.add_argument("--primary-key", default=None)
    etl_parser.add_argument("--hash-column", default="row_hash")
    etl_parser.add_argument("--extract-chunk-size", type=int, default=None)
    etl_parser.add_argument("--write-chunk-size", type=int, default=None)

    ingest_parser = subparsers.add_parser("run-jobs-ingestion")
    ingest_parser.add_argument("--dataset", default="jobs")
    ingest_parser.add_argument("--dt", default=None)
    ingest_parser.add_argument("--run-id", default=None)

    ai_index_parser = subparsers.add_parser("run-ai-indexing")
    ai_index_parser.add_argument("--profile", choices=AI_PROFILE_NAMES, default=None)

    ask_parser = subparsers.add_parser("answer-query")
    ask_parser.add_argument("--question", required=True)
    ask_parser.add_argument("--profile", choices=AI_PROFILE_NAMES, default=None)
    ask_parser.add_argument("--top-k", type=int, default=None)

    grounded_ask_parser = subparsers.add_parser("ask-ai")
    grounded_ask_parser.add_argument("--question", required=True)
    grounded_ask_parser.add_argument("--profile", choices=AI_PROFILE_NAMES, default=None)
    grounded_ask_parser.add_argument("--top-k", type=int, default=None)
    grounded_ask_parser.add_argument("--fetch-k", type=int, default=None)

    args = parser.parse_args()

    if args.command == "run-etl":
        run_etl(
            profile=args.profile,
            load_mode=args.load_mode,
            write_mode=args.write_mode,
            date_column=args.date_column,
            primary_key=args.primary_key,
            hash_column=args.hash_column,
            extract_chunk_size=args.extract_chunk_size,
            write_chunk_size=args.write_chunk_size,
        )
    elif args.command == "run-jobs-ingestion":
        output_file = run_jobs_ingestion(
            dataset=args.dataset,
            dt=args.dt,
            run_id=args.run_id,
        )
        print(f"Ingestion completed. File saved at: {output_file}")
    elif args.command == "run-ai-indexing":
        run_ai_indexing(profile=args.profile)
    elif args.command == "answer-query":
        print(
            answer_query(
                question=args.question,
                profile=args.profile,
                top_k=args.top_k,
            )
        )
    elif args.command == "ask-ai":
        print(
            ask_ai(
                question=args.question,
                profile=args.profile,
                top_k=args.top_k,
                fetch_k=args.fetch_k,
            )
        )


if __name__ == "__main__":
    main()
