from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any

from src.domain.pipeline_editor.models import PipelineNode


class NodeExecutor(ABC):
    @abstractmethod
    def execute(self, node: PipelineNode, context: dict[str, Any]) -> dict[str, Any]:
        raise NotImplementedError
