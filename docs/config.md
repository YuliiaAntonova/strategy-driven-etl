# Configuration

## sources.yml

```yaml
sources:
  jobs_api_berlin:
    type: jobs_api
    config:
      search_term: data engineer
      location: Berlin
```

## destinations.yml

```yaml
destinations:
  local_postgres:
    type: postgres
    credentials:
      host: localhost
```

## options.yml

```yaml
options:
  jobs_load:
    table_name: jobs

    load_behavior:
      profile: historized_snapshot

    runtime:
      use_chunks: true
```
