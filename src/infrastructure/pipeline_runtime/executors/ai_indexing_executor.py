from __future__ import annotations

from typing import Any

from src.application.use_cases.run_ai_indexing import run_ai_indexing
from src.domain.pipeline_editor.models import PipelineNode
from src.domain.pipeline_runtime.executors import NodeExecutor


class AiIndexingExecutor(NodeExecutor):
    def execute(self, node: PipelineNode, context: dict[str, Any]) -> dict[str, Any]:
        config = node.config or {}

        summary = run_ai_indexing(
            profile=config.get("profile"),
        )

        result = dict(summary)
        context[node.id] = result
        return result
