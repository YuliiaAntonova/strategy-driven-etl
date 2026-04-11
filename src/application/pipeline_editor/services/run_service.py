from __future__ import annotations

from datetime import datetime, timezone

from src.application.pipeline_editor.schemas import PipelineRunResponse
from src.domain.pipeline_editor.models import PipelineExecutionPlan, PipelineRunRecord, PipelineRunStatus
from src.domain.pipeline_editor.contracts.pipeline_run_repository import BasePipelineRunRepository


class PipelineRunService:
    """Persist lightweight run metadata for the editor and future workers."""

    def __init__(self, run_repository: BasePipelineRunRepository):
        self._run_repository = run_repository

    def start_run(self, pipeline_id: str, triggered_by: str, plan: PipelineExecutionPlan) -> PipelineRunResponse:
        record = PipelineRunRecord(
            pipeline_id=pipeline_id,
            status=PipelineRunStatus.RUNNING,
            logs=[f"Execution plan contains {len(plan.steps)} step(s)."],
            triggered_by=triggered_by,
        )
        self._run_repository.create_run(record)
        record.status = PipelineRunStatus.SUCCEEDED
        record.finished_at = datetime.now(timezone.utc)
        record.logs.append("Run finished successfully in preview mode.")
        self._run_repository.update_run(record)
        return PipelineRunResponse(run_id=record.id, status=record.status)

    def get_run(self, run_id: str) -> PipelineRunRecord | None:
        return self._run_repository.get_run(run_id)

    def list_runs(self, pipeline_id: str) -> list[PipelineRunRecord]:
        return self._run_repository.list_runs(pipeline_id)
