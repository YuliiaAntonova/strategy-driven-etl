from __future__ import annotations

from typing import Any

from src.application.use_cases.run_etl import run_etl
from src.domain.pipeline_editor.models import PipelineDefinition, PipelineNode
from src.domain.pipeline_runtime.executors import NodeExecutor
from src.infrastructure.extractors.csv import CSVExtractor


class EtlExecutor(NodeExecutor):
    def execute(self, node: PipelineNode, context: dict[str, Any]) -> dict[str, Any]:
        config = node.config or {}
        definition = context.get("__pipeline_definition__")

        extractor_node = self._resolve_node_reference(
            definition=definition,
            node_id=config.get("extractor_node_id"),
            expected_prefix="extractor.",
            field_name="extractor_node_id",
        )
        loader_node = self._resolve_node_reference(
            definition=definition,
            node_id=config.get("loader_node_id"),
            expected_prefix="loader.",
            field_name="loader_node_id",
        )

        extractor = self._build_extractor(extractor_node)
        target_table = self._resolve_target_table(loader_node)

        run_etl(
            load_mode=config.get("load_mode", "full"),
            write_mode=config.get("write_mode"),
            date_column=config.get("date_column", "date_loaded"),
            primary_key=config.get("primary_key"),
            hash_column=config.get("hash_column", "row_hash"),
            extract_chunk_size=config.get("extract_chunk_size"),
            write_chunk_size=config.get("write_chunk_size"),
            profile=config.get("profile"),
            extractor=extractor,
            target_table=target_table,
        )

        result = {
            "extractor_node_id": extractor_node.id,
            "loader_node_id": loader_node.id,
            "load_mode": config.get("load_mode", "full"),
            "write_mode": config.get("write_mode"),
            "target_table": target_table,
            "target": "etl_completed",
        }
        context[node.id] = result
        return result

    @staticmethod
    def _resolve_node_reference(
        *,
        definition: PipelineDefinition | None,
        node_id: Any,
        expected_prefix: str,
        field_name: str,
    ) -> PipelineNode:
        if definition is None:
            raise ValueError("Pipeline definition is missing from runtime context.")
        if not isinstance(node_id, str) or not node_id.strip():
            raise ValueError(f"'{field_name}' must reference an existing node.")

        referenced_node = next((candidate for candidate in definition.nodes if candidate.id == node_id), None)
        if referenced_node is None:
            raise ValueError(f"Referenced node '{node_id}' from '{field_name}' was not found.")
        if not referenced_node.type.startswith(expected_prefix):
            raise ValueError(
                f"Referenced node '{node_id}' from '{field_name}' must be of type '{expected_prefix}*'."
            )
        return referenced_node

    @staticmethod
    def _build_extractor(node: PipelineNode):
        config = node.config or {}
        if node.type == "extractor.csv":
            file_path = config.get("file_path")
            if not isinstance(file_path, str) or not file_path.strip():
                raise ValueError("CSV extractor requires a non-empty 'file_path'.")
            return CSVExtractor(file_path=file_path)

        raise ValueError(f"Unsupported extractor node type: {node.type}")

    @staticmethod
    def _resolve_target_table(node: PipelineNode) -> str:
        config = node.config or {}
        if node.type == "loader.postgres":
            table_name = config.get("table")
            if not isinstance(table_name, str) or not table_name.strip():
                raise ValueError("Postgres loader requires a non-empty 'table'.")
            return table_name

        raise ValueError(f"Unsupported loader node type: {node.type}")
