from __future__ import annotations

from fastapi import APIRouter, HTTPException

from src.application.agent.schemas import AgentTaskCreateResponse, AgentTaskRequest, AgentTaskResponse
from src.application.api.dependencies import get_executor, get_planner, get_task_service, get_tool_registry

router = APIRouter(prefix="/tasks", tags=["agent-tasks"])


@router.post("", response_model=AgentTaskCreateResponse)
def create_task(request: AgentTaskRequest) -> AgentTaskCreateResponse:
    planner = get_planner()
    task_service = get_task_service()
    executor = get_executor()

    plan = planner.plan(prompt=request.prompt, requested_profile=request.profile)
    task_id = task_service.create_task(prompt=request.prompt, plan=plan)
    executor.execute_plan(task_id=task_id, plan=plan, dry_run=request.dry_run)
    task = task_service.get_task(task_id)
    if task is None:
        raise HTTPException(status_code=500, detail="Task was created but could not be loaded")
    return AgentTaskCreateResponse(task_id=task_id, status=task["status"], plan=task["plan"])


@router.get("/{task_id}", response_model=AgentTaskResponse)
def get_task(task_id: str) -> AgentTaskResponse:
    task_service = get_task_service()
    task = task_service.get_task(task_id)
    if task is None:
        raise HTTPException(status_code=404, detail="Task not found")
    return AgentTaskResponse(**task)


@router.get("/meta/tools")
def list_tools() -> dict[str, list[dict[str, str]]]:
    return {"tools": get_tool_registry().list_tools()}
