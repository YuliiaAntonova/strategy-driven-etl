from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Any


@dataclass(slots=True)
class ToolContext:
    task_id: str
    dry_run: bool = False


class AgentTool(ABC):
    name: str
    description: str

    @abstractmethod
    def run(self, payload: dict[str, Any], context: ToolContext) -> dict[str, Any]:
        raise NotImplementedError
