from __future__ import annotations

from typing import Any

from src.domain.agent.contracts.task_repository import TaskRepository


class AgentTaskService:
    def __init__(self, task_repository: TaskRepository) -> None:
        self.task_repository = task_repository

    def create_task(self, prompt: str, plan: list[dict[str, Any]]) -> str:
        return self.task_repository.create_task(prompt=prompt, plan=plan)

    def mark_running(self, task_id: str) -> None:
        self.task_repository.update_task_status(task_id=task_id, status="running")

    def mark_completed(self, task_id: str, result: dict[str, Any]) -> None:
        self.task_repository.complete_task(task_id=task_id, result=result)

    def mark_failed(self, task_id: str, error: str) -> None:
        self.task_repository.fail_task(task_id=task_id, error=error)

    def start_step(self, task_id: str, step_no: int, tool_name: str, input_data: dict[str, Any]) -> None:
        self.task_repository.start_step(task_id=task_id, step_no=step_no, tool_name=tool_name, input_data=input_data)

    def finish_step(self, task_id: str, step_no: int, output_data: dict[str, Any]) -> None:
        self.task_repository.finish_step(task_id=task_id, step_no=step_no, output_data=output_data)

    def fail_step(self, task_id: str, step_no: int, error: str) -> None:
        self.task_repository.fail_step(task_id=task_id, step_no=step_no, error=error)

    def get_task(self, task_id: str) -> dict[str, Any] | None:
        return self.task_repository.get_task(task_id=task_id)
