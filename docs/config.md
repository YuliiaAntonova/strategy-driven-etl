# Configuration

Runtime reads YAML from ``config/`` via ``ProfileLoader``.

## connectors.yml

Holds **all** connector profiles used as ``source_profile`` or ``destination_profile`` (API, CSV, Postgres, Snowflake, etc.). Example:

```yaml
connectors:
  jobs_api_berlin:
    type: jobs_api
    roles: [extractor]
    resource_name: jobs
    config:
      search_term: data scientist
      location: Berlin
      results_wanted: 10

  local_postgres:
    type: postgres
    roles: [extractor, loader]
    credentials:
      host: localhost
      database: mydb
      user: postgres
      password: secret
```

## options.yml

Pipeline options: top-level ``table_name``, ``transforms``, ``load_behavior``, ``runtime``.

Under ``load_behavior`` the runtime reads only: ``profile``, ``primary_key``, ``date_column``, ``hash_column``, ``hash_columns``. Other keys are ignored unless you extend the application spec builder.

```yaml
options:
  jobs_load:
    table_name: jobs

    load_behavior:
      profile: historized_snapshot   # full_refresh | historized_snapshot | incremental_upsert
      primary_key: id
      hash_columns:
        - title
        - company

    runtime:
      extract_chunk_size: 500
      write_chunk_size: 1000
```
