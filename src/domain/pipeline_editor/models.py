from __future__ import annotations

from datetime import datetime, timezone
from enum import Enum
from typing import Any
from uuid import uuid4

from pydantic import BaseModel, Field, field_validator, model_validator


class PipelineNodePosition(BaseModel):
    x: float = 0
    y: float = 0


class PipelineNode(BaseModel):
    id: str
    type: str
    name: str
    position: PipelineNodePosition = Field(default_factory=PipelineNodePosition)
    config: dict[str, Any] = Field(default_factory=dict)


class PipelineEdge(BaseModel):
    source: str
    target: str


class PipelineDefinition(BaseModel):
    id: str
    name: str
    description: str | None = None
    version: int = 1
    nodes: list[PipelineNode] = Field(default_factory=list)
    edges: list[PipelineEdge] = Field(default_factory=list)
    tags: list[str] = Field(default_factory=list)
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

    @field_validator("id", "name")
    @classmethod
    def ensure_non_empty_strings(cls, value: str) -> str:
        if not value or not value.strip():
            raise ValueError("value must not be empty")
        return value.strip()

    @model_validator(mode="after")
    def ensure_unique_node_ids(self) -> "PipelineDefinition":
        node_ids = [node.id for node in self.nodes]
        duplicates = {node_id for node_id in node_ids if node_ids.count(node_id) > 1}
        if duplicates:
            raise ValueError(f"duplicate node ids found: {sorted(duplicates)}")
        return self


class PipelineDefinitionSummary(BaseModel):
    id: str
    name: str
    description: str | None = None
    version: int
    node_count: int
    edge_count: int
    updated_at: datetime


class ValidationSeverity(str, Enum):
    ERROR = "error"
    WARNING = "warning"


class ValidationIssue(BaseModel):
    code: str
    message: str
    severity: ValidationSeverity
    node_id: str | None = None
    edge: PipelineEdge | None = None


class PipelineValidationResult(BaseModel):
    valid: bool
    issues: list[ValidationIssue] = Field(default_factory=list)


class NodeConfigField(BaseModel):
    name: str
    type: str
    required: bool = False
    description: str | None = None
    default: Any | None = None
    options: list[str | dict[str, str]] = Field(default_factory=list)


class NodeTypeDefinition(BaseModel):
    type: str
    label: str
    category: str
    description: str
    config_fields: list[NodeConfigField] = Field(default_factory=list)


class PipelineRunStatus(str, Enum):
    PENDING = "pending"
    RUNNING = "running"
    SUCCEEDED = "succeeded"
    FAILED = "failed"


class NodeRunRecord(BaseModel):
    node_id: str
    node_type: str
    status: PipelineRunStatus = PipelineRunStatus.PENDING
    started_at: datetime | None = None
    finished_at: datetime | None = None
    output: dict[str, Any] = Field(default_factory=dict)
    error_message: str | None = None
    logs: list[str] = Field(default_factory=list)


class PipelineRunRecord(BaseModel):
    id: str = Field(default_factory=lambda: uuid4().hex)
    pipeline_id: str
    status: PipelineRunStatus = PipelineRunStatus.PENDING
    started_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    finished_at: datetime | None = None
    logs: list[str] = Field(default_factory=list)
    triggered_by: str = "api"
    error_message: str | None = None
    node_runs: list[NodeRunRecord] = Field(default_factory=list)


class BuildPlanStep(BaseModel):
    node_id: str
    node_type: str
    action: str
    dependencies: list[str] = Field(default_factory=list)


class PipelineExecutionPlan(BaseModel):
    pipeline_id: str
    steps: list[BuildPlanStep] = Field(default_factory=list)
