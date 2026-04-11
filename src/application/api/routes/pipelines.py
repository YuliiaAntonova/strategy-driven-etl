from __future__ import annotations

from fastapi import APIRouter, HTTPException

from src.application.api.dependencies import (
    get_node_catalog_service,
    get_pipeline_definition_service,
    get_pipeline_runtime_run_service,
    get_pipeline_validation_service,
)
from src.application.pipeline_editor.schemas import CreatePipelineRequest, PipelineRunResponse, RunPipelineRequest, SavePipelineRequest
from src.domain.pipeline_editor.models import PipelineDefinition, PipelineRunRecord

router = APIRouter(prefix="/pipelines", tags=["pipelines"])


@router.get("")
def list_pipelines() -> dict[str, list[dict]]:
    service = get_pipeline_definition_service()
    summaries = service.list_pipelines()
    return {"items": [summary.model_dump(mode="json") for summary in summaries]}


@router.post("", response_model=PipelineDefinition)
def create_pipeline(request: CreatePipelineRequest) -> PipelineDefinition:
    service = get_pipeline_definition_service()
    existing = service.get_pipeline(request.id)
    if existing is not None:
        raise HTTPException(status_code=409, detail="Pipeline already exists")
    return service.create_pipeline(request)


@router.get("/meta/node-types")
def list_node_types() -> dict[str, list[dict]]:
    service = get_node_catalog_service()
    node_types = service.list_node_types()
    return {"items": [node_type.model_dump(mode="json") for node_type in node_types]}


@router.get("/{pipeline_id}", response_model=PipelineDefinition)
def get_pipeline(pipeline_id: str) -> PipelineDefinition:
    service = get_pipeline_definition_service()
    definition = service.get_pipeline(pipeline_id)
    if definition is None:
        raise HTTPException(status_code=404, detail="Pipeline not found")
    return definition


@router.put("/{pipeline_id}", response_model=PipelineDefinition)
def save_pipeline(pipeline_id: str, request: SavePipelineRequest) -> PipelineDefinition:
    service = get_pipeline_definition_service()
    return service.save_pipeline(pipeline_id, request)


@router.delete("/{pipeline_id}", status_code=204)
def delete_pipeline(pipeline_id: str) -> None:
    service = get_pipeline_definition_service()
    service.delete_pipeline(pipeline_id)


@router.post("/{pipeline_id}/validate")
def validate_pipeline(pipeline_id: str) -> dict:
    definition_service = get_pipeline_definition_service()
    validation_service = get_pipeline_validation_service()
    definition = definition_service.get_pipeline(pipeline_id)
    if definition is None:
        raise HTTPException(status_code=404, detail="Pipeline not found")
    result = validation_service.validate(definition)
    return result.model_dump(mode="json")


@router.post("/{pipeline_id}/run", response_model=PipelineRunResponse)
def run_pipeline(pipeline_id: str, request: RunPipelineRequest) -> PipelineRunResponse:
    definition_service = get_pipeline_definition_service()
    validation_service = get_pipeline_validation_service()
    runtime_run_service = get_pipeline_runtime_run_service()

    definition = definition_service.get_pipeline(pipeline_id)
    if definition is None:
        raise HTTPException(status_code=404, detail="Pipeline not found")

    validation = validation_service.validate(definition)
    if not validation.valid:
        raise HTTPException(status_code=400, detail=validation.model_dump(mode="json"))

    return runtime_run_service.run_pipeline(
        definition=definition,
        triggered_by=request.triggered_by,
    )


@router.get("/{pipeline_id}/runs")
def list_runs(pipeline_id: str) -> dict[str, list[dict]]:
    run_service = get_pipeline_runtime_run_service()
    runs = run_service.list_runs(pipeline_id)
    return {"items": [run.model_dump(mode="json") for run in runs]}


@router.get("/runs/{run_id}", response_model=PipelineRunRecord)
def get_run(run_id: str) -> PipelineRunRecord:
    run_service = get_pipeline_runtime_run_service()
    run = run_service.get_run(run_id)
    if run is None:
        raise HTTPException(status_code=404, detail="Run not found")
    return run
