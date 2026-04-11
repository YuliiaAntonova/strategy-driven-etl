# Visual pipeline editor architecture

## Why this layer exists
The existing ETL runtime remains focused on execution.
The new visual editor layer owns only:
- editable pipeline definitions
- validation of graph structure
- node catalog exposure for UI
- run metadata for editor feedback

This separation keeps the system aligned with SOLID:

### Single Responsibility
- runtime pipeline code executes data jobs
- editor services manage visual definitions and validation
- repositories persist definitions and runs
- API routes expose use cases only

### Open/Closed
- new repository implementations can replace file or memory storage
- new node catalogs can be added without changing services
- future async run executors can replace preview mode without breaking controllers

### Liskov Substitution
- all repositories and catalogs are accessed through base contracts

### Interface Segregation
- definition storage, run storage, and node catalog are separate contracts

### Dependency Inversion
- application services depend on abstractions from `domain/pipeline_editor/contracts`
- infrastructure provides concrete adapters

## Added backend folders
- `src/domain/pipeline_editor/`
- `src/application/pipeline_editor/`
- `src/infrastructure/pipeline_editor/`
- `src/application/api/routes/pipelines.py`
- `pipelines/`

## Added frontend scaffold folder
- `frontend/`

## Recommended next scaling steps
1. swap in-memory run repository with Postgres
2. add async workers for real runs
3. replace static node catalog with registry-backed catalog
4. add role-based auth around editor endpoints
5. implement React Flow UI in `frontend/`
