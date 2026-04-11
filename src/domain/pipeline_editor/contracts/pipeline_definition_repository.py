from __future__ import annotations

from abc import ABC, abstractmethod

from src.domain.pipeline_editor.models import PipelineDefinition


class BasePipelineDefinitionRepository(ABC):
    """Abstract storage for editable pipeline definitions."""

    @abstractmethod
    def list_definitions(self) -> list[PipelineDefinition]:
        """Return all stored pipeline definitions."""

    @abstractmethod
    def get_definition(self, pipeline_id: str) -> PipelineDefinition | None:
        """Return one pipeline definition if it exists."""

    @abstractmethod
    def save_definition(self, definition: PipelineDefinition) -> PipelineDefinition:
        """Create or replace a pipeline definition."""

    @abstractmethod
    def delete_definition(self, pipeline_id: str) -> None:
        """Delete a pipeline definition if it exists."""
