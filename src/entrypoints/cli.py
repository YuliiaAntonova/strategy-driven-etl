import argparse

from src.application.use_cases.run_etl import run_etl
from src.application.use_cases.run_jobs_ingestion import run_jobs_ingestion
from src.application.services.write_strategy_factory import WRITE_MODES


LOAD_MODES = [
    "full",
    "incremental-by-date",
    "incremental-by-primary-key",
    "incremental-by-hash",
    "incremental-by-primary-key-and-hash",
]


def main():
    parser = argparse.ArgumentParser()

    subparsers = parser.add_subparsers(dest="command", required=True)

    etl_parser = subparsers.add_parser("run-etl")
    etl_parser.add_argument("--load-mode", choices=LOAD_MODES, default="full")
    etl_parser.add_argument("--write-mode", choices=WRITE_MODES, default="replace")
    etl_parser.add_argument("--date-column", default="date_loaded")
    etl_parser.add_argument("--primary-key", default=None)
    etl_parser.add_argument("--hash-column", default="row_hash")

    ingest_parser = subparsers.add_parser("run-jobs-ingestion")
    ingest_parser.add_argument("--dataset", default="jobs")
    ingest_parser.add_argument("--dt", default=None)
    ingest_parser.add_argument("--run-id", default=None)

    args = parser.parse_args()

    if args.command == "run-etl":
        run_etl(
            load_mode=args.load_mode,
            write_mode=args.write_mode,
            date_column=args.date_column,
            primary_key=args.primary_key,
            hash_column=args.hash_column,
        )
    elif args.command == "run-jobs-ingestion":
        output_file = run_jobs_ingestion(
            dataset=args.dataset,
            dt=args.dt,
            run_id=args.run_id,
        )
        print(f"Ingestion completed. File saved at: {output_file}")


if __name__ == "__main__":
    main()
