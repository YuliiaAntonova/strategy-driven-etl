# strategy-driven-etl

A dynamic, profile-driven ETL framework with chunking, historized loading (SCD2), and clean SOLID architecture.

## Quick start

```python
from src import pipeline

p = pipeline(
    pipeline_name="jobs_pipeline",
    source_profile="jobs_api_berlin",
    destination_profile="local_postgres",
    options_profile="jobs_load",
)

p.run()
```

## Configuration

All logic is defined in:

```text
config/
  sources.yml
  destinations.yml
  options.yml
```

## Features

- dynamic sources (API, CSV, Snowflake)
- dynamic destinations (Postgres, etc.)
- full refresh and historized snapshot (SCD2)
- chunked processing
- hash-based change detection
- generated IDs
- SOLID architecture

## Install

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install pandas sqlalchemy psycopg2-binary python-dotenv pyyaml python-jobspy
```

## Run

```bash
python test.py
```

## Docs

See:

```text
docs/
```
