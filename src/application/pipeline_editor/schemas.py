from __future__ import annotations

from pydantic import BaseModel, Field

from src.domain.pipeline_editor.models import PipelineEdge, PipelineNode, PipelineRunStatus


class CreatePipelineRequest(BaseModel):
    id: str
    name: str
    description: str | None = None
    tags: list[str] = Field(default_factory=list)


class SavePipelineRequest(BaseModel):
    name: str
    description: str | None = None
    version: int = 1
    nodes: list[PipelineNode] = Field(default_factory=list)
    edges: list[PipelineEdge] = Field(default_factory=list)
    tags: list[str] = Field(default_factory=list)


class RunPipelineRequest(BaseModel):
    triggered_by: str = "api"


class PipelineRunResponse(BaseModel):
    run_id: str
    status: PipelineRunStatus
