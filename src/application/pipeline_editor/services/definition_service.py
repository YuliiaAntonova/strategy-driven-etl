from __future__ import annotations

from datetime import datetime, timezone

from src.application.pipeline_editor.schemas import CreatePipelineRequest, SavePipelineRequest
from src.domain.pipeline_editor.models import PipelineDefinition, PipelineDefinitionSummary
from src.domain.pipeline_editor.contracts.pipeline_definition_repository import BasePipelineDefinitionRepository


class PipelineDefinitionService:
    """Application service for CRUD over editable pipeline definitions."""

    def __init__(self, repository: BasePipelineDefinitionRepository):
        self._repository = repository

    def list_pipelines(self) -> list[PipelineDefinitionSummary]:
        definitions = self._repository.list_definitions()
        return [
            PipelineDefinitionSummary(
                id=definition.id,
                name=definition.name,
                description=definition.description,
                version=definition.version,
                node_count=len(definition.nodes),
                edge_count=len(definition.edges),
                updated_at=definition.updated_at,
            )
            for definition in definitions
        ]

    def create_pipeline(self, request: CreatePipelineRequest) -> PipelineDefinition:
        definition = PipelineDefinition(
            id=request.id,
            name=request.name,
            description=request.description,
            tags=request.tags,
        )
        return self._repository.save_definition(definition)

    def get_pipeline(self, pipeline_id: str) -> PipelineDefinition | None:
        return self._repository.get_definition(pipeline_id)

    def save_pipeline(self, pipeline_id: str, request: SavePipelineRequest) -> PipelineDefinition:
        existing = self._repository.get_definition(pipeline_id)
        created_at = existing.created_at if existing else datetime.now(timezone.utc)
        definition = PipelineDefinition(
            id=pipeline_id,
            name=request.name,
            description=request.description,
            version=request.version,
            nodes=request.nodes,
            edges=request.edges,
            tags=request.tags,
            created_at=created_at,
            updated_at=datetime.now(timezone.utc),
        )
        return self._repository.save_definition(definition)

    def delete_pipeline(self, pipeline_id: str) -> None:
        self._repository.delete_definition(pipeline_id)

    def update_pipeline(self, pipeline_id: str, payload):
        existing = self._repository.get(pipeline_id)
        if existing is None:
            return None

        updated = existing.model_copy(update=payload.model_dump())
        self._repository.save(updated)
        return updated
