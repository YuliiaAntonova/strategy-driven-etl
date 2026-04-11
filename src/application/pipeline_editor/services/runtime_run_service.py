from __future__ import annotations

from datetime import datetime, timezone

from src.application.pipeline_editor.schemas import PipelineRunResponse
from src.application.pipeline_runtime.runner import VisualPipelineRunner
from src.domain.pipeline_editor.contracts.pipeline_run_repository import BasePipelineRunRepository
from src.domain.pipeline_editor.models import PipelineDefinition, PipelineRunRecord, PipelineRunStatus


class PipelineRuntimeRunService:
    def __init__(
        self,
        run_repository: BasePipelineRunRepository,
        runner: VisualPipelineRunner,
    ):
        self._run_repository = run_repository
        self._runner = runner

    def run_pipeline(self, definition: PipelineDefinition, triggered_by: str) -> PipelineRunResponse:
        record = PipelineRunRecord(
            pipeline_id=definition.id,
            status=PipelineRunStatus.RUNNING,
            logs=["Pipeline run started."],
            triggered_by=triggered_by,
        )
        self._run_repository.create_run(record)

        try:
            node_runs = self._runner.run(definition)
            record.node_runs = node_runs
            record.status = PipelineRunStatus.SUCCEEDED
            record.finished_at = datetime.now(timezone.utc)
            record.logs.append("Pipeline completed successfully.")
            for node_run in node_runs:
                record.logs.append(
                    f"{node_run.node_id} [{node_run.status}] output={node_run.output}"
                )
        except Exception as exc:
            record.status = PipelineRunStatus.FAILED
            record.finished_at = datetime.now(timezone.utc)
            record.error_message = str(exc)
            record.logs.append(f"Pipeline failed: {exc}")
        finally:
            self._run_repository.update_run(record)

        return PipelineRunResponse(
            run_id=record.id,
            status=record.status,
        )

    def get_run(self, run_id: str) -> PipelineRunRecord | None:
        return self._run_repository.get_run(run_id)

    def list_runs(self, pipeline_id: str) -> list[PipelineRunRecord]:
        return self._run_repository.list_runs(pipeline_id)
