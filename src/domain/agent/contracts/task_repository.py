"""Domain contract for persisting and retrieving agent task state."""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any


class TaskRepository(ABC):
    """Repository interface for agent tasks and step-level progress."""

    @abstractmethod
    def create_task(self, prompt: str, plan: list[dict[str, Any]]) -> str:
        """Create a task and return the generated task id."""
        raise NotImplementedError

    @abstractmethod
    def update_task_status(self, task_id: str, status: str) -> None:
        """Update the overall task status (e.g. queued/running/completed/failed)."""
        raise NotImplementedError

    @abstractmethod
    def complete_task(self, task_id: str, result: dict[str, Any]) -> None:
        """Mark a task as completed and persist its final result payload."""
        raise NotImplementedError

    @abstractmethod
    def fail_task(self, task_id: str, error: str) -> None:
        """Mark a task as failed and persist human-readable error details."""
        raise NotImplementedError

    @abstractmethod
    def start_step(
        self,
        task_id: str,
        step_no: int,
        tool_name: str,
        input_data: dict[str, Any],
    ) -> None:
        """Persist that a task step has started (useful for progress tracking)."""
        raise NotImplementedError

    @abstractmethod
    def finish_step(self, task_id: str, step_no: int, output_data: dict[str, Any]) -> None:
        """Persist the output payload for a finished step."""
        raise NotImplementedError

    @abstractmethod
    def fail_step(self, task_id: str, step_no: int, error: str) -> None:
        """Persist an error for a failed step."""
        raise NotImplementedError

    @abstractmethod
    def get_task(self, task_id: str) -> dict[str, Any] | None:
        """Return the stored task record, or None if not found."""
        raise NotImplementedError
