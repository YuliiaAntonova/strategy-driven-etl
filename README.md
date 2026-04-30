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

All profile-driven behavior is defined in:

```text
config/
  connectors.yml   # source & destination connector profiles (single file)
  options.yml        # dataset name, load behavior, runtime (chunks, etc.)
```

### connectors.yml

Use one profile per named source or destination. Optional ``roles: [extractor, loader]`` documents intent; the runtime selects ``create_extractor`` / ``create_loader`` by connector type.

## Features

- dynamic sources (API, CSV, Snowflake)
- dynamic destinations (Postgres, etc.)
- full refresh, historized snapshot (SCD2), incremental upsert (Postgres)
- chunked processing
- hash-based change detection
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
