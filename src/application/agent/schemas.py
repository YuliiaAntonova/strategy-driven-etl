from __future__ import annotations

from typing import Any

from pydantic import BaseModel, Field


class AgentTaskRequest(BaseModel):
    prompt: str = Field(..., description="Natural language command for the ETL/AI agent")
    profile: str | None = Field(default=None, description="Optional ETL or AI profile override")
    dry_run: bool = Field(default=False, description="Plan the task without executing tools")


class AgentTaskCreateResponse(BaseModel):
    task_id: str
    status: str
    plan: list[dict[str, Any]]


class AgentStepResponse(BaseModel):
    step_no: int
    tool_name: str
    status: str
    input_data: dict[str, Any] = Field(default_factory=dict)
    output_data: dict[str, Any] = Field(default_factory=dict)
    error: str | None = None


class AgentTaskResponse(BaseModel):
    task_id: str
    prompt: str
    status: str
    plan: list[dict[str, Any]] = Field(default_factory=list)
    result: dict[str, Any] = Field(default_factory=dict)
    error: str | None = None
    steps: list[AgentStepResponse] = Field(default_factory=list)
