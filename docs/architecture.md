# Architecture

Pipeline flow:

```text
config → ProfileLoader → PipelineBootstrapConfig → PipelineSpec → RuntimeBuilder → Pipeline
```

Bootstrap inputs are grouped in ``PipelineBootstrapConfig`` (see ``pipeline_bootstrap.py``). Registries for connectors and transforms share ``KeyedRegistry`` for keyed lookups. Reading existing target state uses ``select_star_from_single_table(destination_type, ...)`` so dialect-specific SQL can evolve in one place.

Core components:

- Extractor
- Transformer
- ChangeDetector
- Writer

Pipeline depends on interfaces, not implementations.
