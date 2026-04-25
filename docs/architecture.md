# Architecture

Pipeline flow:

```text
config → ProfileLoader → PipelineSpec → RuntimeBuilder → Pipeline
```

Core components:

- Extractor
- Transformer
- ChangeDetector
- Writer

Pipeline depends on interfaces, not implementations.
