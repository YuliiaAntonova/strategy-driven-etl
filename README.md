# solid_etl_refactor_template

A refactoring template for an ETL/ingestion project.

## What has been updated

- a unified contract: `extract() -> DataFrame`
- a shared `run_pipeline()` for orchestration
- `JobsAuditTransformer`, which:
  - normalizes columns
  - adds `source_name`
  - adds `run_id`
  - adds `dt`
  - adds `date_created`
  - adds `date_loaded`
  - adds `environment`
- `HashColumnsTransformer` for calculating `row_hash`
- several load strategies:
  - `full`
  - `incremental-by-date`
  - `incremental-by-primary-key`
  - `incremental-by-hash`
  - `incremental-by-primary-key-and-hash`
- strategy selection through CLI
- `PostgresLoader` writes to Postgres via SQLAlchemy
- configuration moved to `.env`

## System column logic

Two separate technical dates are written into the table:

- `date_created` — the date when the record first appeared
- `date_loaded` — the date when the current version of the record was loaded

`row_hash` is calculated only from business columns listed in `HASH_COLUMNS`.
`date_created` and `date_loaded` are **not included** in the hash.

Behavior for `incremental-by-primary-key-and-hash`:

- if the `primary_key` is new -> the record is inserted, `date_created = date_loaded`
- if the `primary_key` already exists and `row_hash` has not changed -> the record is not loaded
- if the `primary_key` already exists and `row_hash` has changed -> a new version is inserted, the old `date_created` is preserved, and a new `date_loaded` is set to the current time

## Structure

```text
src/
  application/
    services/
      load_strategy_factory.py
    use_cases/
      run_etl.py
      run_jobs_ingestion.py
      run_pipeline.py
  domain/
    contracts/
      connector.py
      extractor.py
      load_strategy.py
      loader.py
      transformer.py
    models/
      pipeline_context.py
  infrastructure/
    connectors/
      postgres.py
      s3.py
    extractors/
      csv.py
      jobs_api.py
      postgres.py
    loaders/
      csv.py
      postgres.py
      s3.py
    transformers/
      dataframe.py
      hash_columns.py
      jobs.py
    versioning/
      full_load.py
      incremental_by_date.py
      incremental_by_hash.py
      incremental_by_primary_key.py
      incremental_by_primary_key_and_hash.py
  config/
    settings.py
  entrypoints/
    cli.py
    api.py
```

## Running

```bash
python3 -m venv .venv
source .venv/bin/activate
python3 -m pip install -U pip
python3 -m pip install pandas sqlalchemy psycopg2-binary python-dotenv python-jobspy
```

### 1. Jobs ingestion -> local CSV
```bash
python3 -m src.entrypoints.cli run-jobs-ingestion
```

### 2. Full load: CSV -> Postgres
```bash
python3 -m src.entrypoints.cli run-etl --load-mode full
```

### 3. Incremental by date
```bash
python3 -m src.entrypoints.cli run-etl --load-mode incremental-by-date --date-column date_loaded
```

### 4. Incremental by primary key
```bash
python3 -m src.entrypoints.cli run-etl --load-mode incremental-by-primary-key --primary-key job_url
```

### 5. Incremental by hash
```bash
python3 -m src.entrypoints.cli run-etl --load-mode incremental-by-hash --hash-column row_hash
```

### 6. Incremental by primary key + hash
```bash
python3 -m src.entrypoints.cli run-etl --load-mode incremental-by-primary-key-and-hash --primary-key job_url --hash-column row_hash

python3 -m src.entrypoints.cli run-etl \
  --load-mode incremental-by-primary-key-and-hash \
  --write-mode versioned \
  --primary-key job_url \
  --hash-column row_hash
```

## Strategy behavior

- `full` -> `replace`
- all `incremental-*` -> `append`

## Env

Create a `.env` file next to the project:

```env
SOURCE_FILE=data/jobs.csv
POSTGRES_HOST=localhost
POSTGRES_PORT=5432
POSTGRES_DB=world
POSTGRES_USER=postgres
POSTGRES_PASSWORD=postgres
TARGET_TABLE=jobs
JOBS_SEARCH_TERM=data engineer
JOBS_LOCATION=Berlin
JOBS_RESULTS_WANTED=100
SOURCE_NAME=jobs_api
ENVIRONMENT=local
HASH_COLUMNS=title,company,location,job_type,description,min_amount,max_amount,currency
```

## Important

If the table was created earlier without `row_hash`, `date_created`, or `date_loaded`, it is better to recreate it once with:

```bash
psql -h localhost -U postgres -d world -c "drop table if exists jobs;"
python3 -m src.entrypoints.cli run-etl --load-mode full
```

Versioned write mode uses a staging table named `{table_name}_temp` and performs SQL `UPDATE + INSERT` from staging into the target table.

## Write modes

This template now supports SQL-based write strategies through `src/infrastructure/writing/` and `--write-mode`:

- `replace` — stage into `{table_name}_temp`, drop target, rename temp to target
- `append` — stage into `{table_name}_temp`, then `INSERT INTO target SELECT ... FROM temp`
- `upsert` — stage into `{table_name}_temp`, then `INSERT ... ON CONFLICT DO UPDATE` using the primary key
- `versioned` — stage into `{table_name}_temp`, then close old current rows and insert new versions

Example:

```bash
python3 -m src.entrypoints.cli run-etl --load-mode incremental-by-primary-key-and-hash --write-mode versioned --primary-key job_url --hash-column row_hash
```
