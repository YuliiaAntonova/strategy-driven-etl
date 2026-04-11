from __future__ import annotations

from src.domain.pipeline_editor.models import PipelineRunRecord
from src.domain.pipeline_editor.contracts.pipeline_run_repository import BasePipelineRunRepository


class InMemoryPipelineRunRepository(BasePipelineRunRepository):
    """Simple run storage that can later be swapped for SQL without touching services."""

    def __init__(self):
        self._records: dict[str, PipelineRunRecord] = {}

    def create_run(self, record: PipelineRunRecord) -> PipelineRunRecord:
        self._records[record.id] = record
        return record

    def update_run(self, record: PipelineRunRecord) -> PipelineRunRecord:
        self._records[record.id] = record
        return record

    def get_run(self, run_id: str) -> PipelineRunRecord | None:
        return self._records.get(run_id)

    def list_runs(self, pipeline_id: str) -> list[PipelineRunRecord]:
        return [record for record in self._records.values() if record.pipeline_id == pipeline_id]
