from __future__ import annotations

import json
from pathlib import Path

from src.domain.pipeline_editor.models import PipelineDefinition
from src.domain.pipeline_editor.contracts.pipeline_definition_repository import BasePipelineDefinitionRepository


class FilePipelineDefinitionRepository(BasePipelineDefinitionRepository):
    """File-based storage that keeps the visual definition independent from runtime code."""

    def __init__(self, base_path: str | Path = "pipelines"):
        self._base_path = Path(base_path)
        self._base_path.mkdir(parents=True, exist_ok=True)

    def list_definitions(self) -> list[PipelineDefinition]:
        definitions: list[PipelineDefinition] = []
        for file_path in sorted(self._base_path.glob("*.json")):
            definitions.append(self._read_file(file_path))
        return definitions

    def get_definition(self, pipeline_id: str) -> PipelineDefinition | None:
        file_path = self._file_path(pipeline_id)
        if not file_path.exists():
            return None
        return self._read_file(file_path)

    def save_definition(self, definition: PipelineDefinition) -> PipelineDefinition:
        file_path = self._file_path(definition.id)
        file_path.write_text(definition.model_dump_json(indent=2), encoding="utf-8")
        return definition

    def delete_definition(self, pipeline_id: str) -> None:
        file_path = self._file_path(pipeline_id)
        if file_path.exists():
            file_path.unlink()

    def _file_path(self, pipeline_id: str) -> Path:
        return self._base_path / f"{pipeline_id}.json"

    @staticmethod
    def _read_file(file_path: Path) -> PipelineDefinition:
        raw_data = json.loads(file_path.read_text(encoding="utf-8"))
        return PipelineDefinition.model_validate(raw_data)

    def save(self, definition):
        path = self._base_path / f"{definition.id}.json"
        with open(path, "w") as f:
            f.write(definition.model_dump_json(indent=2))