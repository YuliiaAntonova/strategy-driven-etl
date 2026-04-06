from __future__ import annotations

from typing import Any

from src.application.agent.tools.base import AgentTool, ToolContext
from src.application.use_cases.run_jobs_ingestion import run_jobs_ingestion


class RunJobsIngestionTool(AgentTool):
    name = "run_jobs_ingestion"
    description = "Ingest fresh jobs data into the source file used by the ETL pipeline"

    def run(self, payload: dict[str, Any], context: ToolContext) -> dict[str, Any]:
        if context.dry_run:
            return {"message": "Dry run: jobs ingestion would be executed", "payload": payload}

        output_file = run_jobs_ingestion(
            dataset=payload.get("dataset", "jobs"),
            dt=payload.get("dt"),
            run_id=payload.get("run_id"),
        )
        return {"message": "Jobs ingestion completed", "output_file": output_file}
