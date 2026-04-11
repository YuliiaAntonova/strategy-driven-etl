from __future__ import annotations

from abc import ABC, abstractmethod

from src.domain.pipeline_editor.models import PipelineRunRecord


class BasePipelineRunRepository(ABC):
    """Abstract storage for pipeline run metadata."""

    @abstractmethod
    def create_run(self, record: PipelineRunRecord) -> PipelineRunRecord:
        """Persist a newly created run record."""

    @abstractmethod
    def update_run(self, record: PipelineRunRecord) -> PipelineRunRecord:
        """Persist changes for an existing run record."""

    @abstractmethod
    def get_run(self, run_id: str) -> PipelineRunRecord | None:
        """Return a run by identifier."""

    @abstractmethod
    def list_runs(self, pipeline_id: str) -> list[PipelineRunRecord]:
        """Return all runs for a pipeline."""
