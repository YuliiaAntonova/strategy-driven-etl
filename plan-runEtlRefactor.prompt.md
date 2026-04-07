## Goal
Refactor `src/application/use_cases/run_etl.py` to better follow SOLID (single responsibility), reduce number of parameters/locals, and keep CLI behavior stable.

## Constraints
- Keep `python -m src.entrypoints.cli run-etl ...` flags and behavior unchanged.
- Prefer additive refactor (new modules) + thin facade in `run_etl.py`.
- Do not change domain contracts unless necessary.

## Current problems (from pylint)
- `run_etl.py` has:
  - too many arguments (`R0913`, `R0917`)
  - too many locals (`R0914`)
  - broad exception catch (`W0718`)
  - long lines
- Function likely mixes responsibilities:
  - CLI validation
  - profile/settings resolution
  - connector construction
  - pipeline wiring
  - chunk loop/IO
  - writing + optional snowflake loading

## Proposed refactor
Split into: config object + resolver + builder + optional error mapping.

### 1) Introduce `RunEtlConfig`
Create `src/application/use_cases/etl/config.py`:
- `@dataclass(frozen=True)` `RunEtlConfig`
- Fields mirror CLI args plus derived values
  - `profile: str | None`
  - `load_mode: str`
  - `write_mode: str`
  - `primary_key: str | None`
  - `date_column: str | None`
  - `hash_column: str | None`
  - `extract_chunk_size: int | None`
  - `write_chunk_size: int | None`
  - `use_snowflake: bool`
  - overrides for testing: `connector_override` / `extractor_override` etc. (optional)
- `validate()` method encapsulates parameter validation.

### 2) Profile resolution module
Create `src/application/use_cases/etl/profile_resolution.py`:
- `resolve_runtime_profile(config, settings)` returns a runtime profile object
- Keeps all mapping logic out of the use case.

### 3) Pipeline builder
Create `src/application/use_cases/etl/pipeline_builder.py`:
- `EtlPipelineBuilder(settings, registries...)`
- `build(config) -> Pipeline`
- Owns wiring:
  - connectors
  - extractors
  - transformers
  - change detectors
  - loaders/writers
  - optional snowflake loader

### 4) State reader / existing-data retrieval
Create `src/application/use_cases/etl/state_reader.py`:
- Encapsulates reading existing target state and fallback-to-empty behavior.
- Helps keep pipeline run loop clean.

### 5) Error mapping
Create `src/application/use_cases/etl/errors.py`:
- map low-level exceptions to stable user-facing messages
- avoid `except Exception` in the core use case

### 6) Keep `run_etl.py` as a thin facade
- Keep public `run_etl(...)` signature for CLI stability.
- Implementation:
  1) build `RunEtlConfig` from args
  2) `config.validate()`
  3) `profile = resolve_runtime_profile(...)`
  4) pipeline = builder.build(config)
  5) `pipeline.run(extract_chunk_size=...)`

## Decisions to confirm during implementation
- Logging behavior when target table is missing (silent vs warning).
- Whether to keep optional `connector` injection in signature or move to config override.

## Acceptance criteria
- CLI runs unchanged.
- Pylint warnings in `run_etl.py` reduced: fewer args/locals, no broad exception.
- Tests (if any) still pass; basic CLI run doesn’t crash.

