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

## Main commands

### 1. Jobs ingestion -> local CSV
Downloads jobs and saves them into the source CSV file.

```bash
python3 -m src.entrypoints.cli run-jobs-ingestion
```

### 2. Full load: CSV -> Postgres
Loads the whole source file into Postgres.

```bash
python3 -m src.entrypoints.cli run-etl --load-mode full
```

### 3. Incremental by date
Loads only rows newer than the max value in the target date column.

```bash
python3 -m src.entrypoints.cli run-etl \
  --load-mode incremental-by-date \
  --date-column date_loaded
```

### 4. Incremental by primary key
Loads only rows whose primary key does not yet exist in the target table.

```bash
python3 -m src.entrypoints.cli run-etl \
  --load-mode incremental-by-primary-key \
  --primary-key job_url
```

### 5. Incremental by hash
Loads only rows whose `row_hash` does not yet exist in the target table.

```bash
python3 -m src.entrypoints.cli run-etl \
  --load-mode incremental-by-hash \
  --hash-column row_hash
```

### 6. Incremental by primary key + hash
Loads new rows and changed rows.

```bash
python3 -m src.entrypoints.cli run-etl \
  --load-mode incremental-by-primary-key-and-hash \
  --primary-key job_url \
  --hash-column row_hash
```

### 7. Incremental by primary key + hash with versioned write
Creates a new version only when the row with the same primary key changed.

```bash
python3 -m src.entrypoints.cli run-etl \
  --load-mode incremental-by-primary-key-and-hash \
  --write-mode versioned \
  --primary-key job_url \
  --hash-column row_hash
```

## Write modes

This template supports SQL-based write strategies through `src/infrastructure/writing/` and `--write-mode`:

- `replace` — stage into `{table_name}_temp`, drop target, rename temp to target
- `append` — stage into `{table_name}_temp`, then `INSERT INTO target SELECT ... FROM temp`
- `upsert` — stage into `{table_name}_temp`, then `INSERT ... ON CONFLICT DO UPDATE` using the primary key
- `versioned` — stage into `{table_name}_temp`, then close old current rows and insert new versions

## Recommended command combinations

### Full + replace
Best for first load or full rebuild of the table.

```bash
python3 -m src.entrypoints.cli run-etl \
  --load-mode full \
  --write-mode replace
```

### Full + append
Adds the whole file again. Useful only when you really want duplicate history.

```bash
python3 -m src.entrypoints.cli run-etl \
  --load-mode full \
  --write-mode append
```

### Full + append + chunks
Same as full append, but extraction and writing are split into batches.

```bash
python3 -m src.entrypoints.cli run-etl \
  --load-mode full \
  --write-mode append \
  --extract-chunk-size 10000 \
  --write-chunk-size 5000
```

Example output:

```text
Appended 20 rows into 'jobs' from staging 'jobs_temp'
```

### Incremental by primary key + upsert
Keeps one current row per primary key and updates it on conflict.

```bash
python3 -m src.entrypoints.cli run-etl \
  --load-mode incremental-by-primary-key \
  --write-mode upsert \
  --primary-key job_url
```

### Incremental by primary key + hash + versioned
Best choice when you need row history.

```bash
python3 -m src.entrypoints.cli run-etl \
  --load-mode incremental-by-primary-key-and-hash \
  --write-mode versioned \
  --primary-key job_url \
  --hash-column row_hash
```

## Chunk options

- `--extract-chunk-size` — how many rows to read from the source in one batch
- `--write-chunk-size` — how many rows to write into Postgres in one batch

Example with chunks:

```bash
python3 -m src.entrypoints.cli run-etl \
  --load-mode full \
  --write-mode append \
  --extract-chunk-size 10000 \
  --write-chunk-size 5000
```

Use chunk options when:

- the source file is large
- you want lower memory usage
- you want more controlled writes to Postgres

## Strategy behavior

Default behavior without explicit `--write-mode`:

- `full` -> `replace`
- all `incremental-*` -> `append`

That means:

- `full + append` can create duplicates if you run the same load many times
- `incremental-by-primary-key-and-hash + versioned` does not load unchanged rows

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

If old duplicates were already inserted with `full + append`, recreate the table once and then switch to a safer mode such as `upsert` or `versioned`.

Versioned write mode uses a staging table named `{table_name}_temp` and performs SQL `UPDATE + INSERT` from staging into the target table.
