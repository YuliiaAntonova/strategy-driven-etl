from __future__ import annotations

from typing import Any

from src.application.use_cases.run_jobs_ingestion import run_jobs_ingestion
from src.domain.pipeline_editor.models import PipelineNode
from src.domain.pipeline_runtime.executors import NodeExecutor


class JobsIngestionExecutor(NodeExecutor):
    def execute(self, node: PipelineNode, context: dict[str, Any]) -> dict[str, Any]:
        config = node.config or {}

        output_file = run_jobs_ingestion(
            dataset=config.get("dataset", "jobs"),
            dt=config.get("dt"),
            run_id=config.get("run_id"),
        )

        result = {
            "dataset": config.get("dataset", "jobs"),
            "output_file": output_file,
        }
        context[node.id] = result
        return result
