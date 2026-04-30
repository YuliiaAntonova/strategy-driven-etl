# Load modes

## full_refresh

- replaces table
- no history

## historized_snapshot

- SCD2 behavior
- keeps history
- uses hash

Recommended for production.

## incremental_upsert

- detector: new rows by primary key
- Postgres `ON CONFLICT` upsert (Snowflake не поддержан для этого режима)
