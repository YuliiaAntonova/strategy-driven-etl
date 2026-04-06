from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any


class TaskRepository(ABC):
    @abstractmethod
    def create_task(self, prompt: str, plan: list[dict[str, Any]]) -> str:
        raise NotImplementedError

    @abstractmethod
    def update_task_status(self, task_id: str, status: str) -> None:
        raise NotImplementedError

    @abstractmethod
    def complete_task(self, task_id: str, result: dict[str, Any]) -> None:
        raise NotImplementedError

    @abstractmethod
    def fail_task(self, task_id: str, error: str) -> None:
        raise NotImplementedError

    @abstractmethod
    def start_step(self, task_id: str, step_no: int, tool_name: str, input_data: dict[str, Any]) -> None:
        raise NotImplementedError

    @abstractmethod
    def finish_step(self, task_id: str, step_no: int, output_data: dict[str, Any]) -> None:
        raise NotImplementedError

    @abstractmethod
    def fail_step(self, task_id: str, step_no: int, error: str) -> None:
        raise NotImplementedError

    @abstractmethod
    def get_task(self, task_id: str) -> dict[str, Any] | None:
        raise NotImplementedError
