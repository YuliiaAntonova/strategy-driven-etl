from __future__ import annotations

from collections import defaultdict, deque
from datetime import datetime, timezone

from src.domain.pipeline_editor.models import (
    NodeRunRecord,
    PipelineDefinition,
    PipelineRunStatus,
)
from src.infrastructure.pipeline_runtime.registry import NodeExecutorRegistry


class VisualPipelineRunner:
    EXECUTABLE_PREFIXES = ("entry.", "transformer.", "detector.", "ai.")

    def __init__(self, registry: NodeExecutorRegistry):
        self._registry = registry

    def run(self, definition: PipelineDefinition) -> list[NodeRunRecord]:
        node_runs: list[NodeRunRecord] = []
        context: dict[str, object] = {"__pipeline_definition__": definition, "__node_map__": {node.id: node for node in definition.nodes}}
        ordered_nodes = self._topological_sort(definition)

        for node in ordered_nodes:
            if not self._is_executable_node(node.type):
                node_runs.append(
                    NodeRunRecord(
                        node_id=node.id,
                        node_type=node.type,
                        status=PipelineRunStatus.SUCCEEDED,
                        started_at=datetime.now(timezone.utc),
                        finished_at=datetime.now(timezone.utc),
                        output={"skipped": True, "reason": "resource_node"},
                        logs=[f"Skipping resource node '{node.name}' ({node.type})."],
                    )
                )
                continue

            node_run = NodeRunRecord(
                node_id=node.id,
                node_type=node.type,
                status=PipelineRunStatus.RUNNING,
                started_at=datetime.now(timezone.utc),
                logs=[f"Executing node '{node.name}' ({node.type})"],
            )
            node_runs.append(node_run)

            try:
                executor = self._registry.get(node.type)
                output = executor.execute(node, context)
                node_run.output = output
                node_run.status = PipelineRunStatus.SUCCEEDED
                node_run.logs.append("Node completed successfully.")
            except Exception as exc:
                node_run.status = PipelineRunStatus.FAILED
                node_run.error_message = str(exc)
                node_run.logs.append(f"Node failed: {exc}")
                node_run.finished_at = datetime.now(timezone.utc)
                raise
            else:
                node_run.finished_at = datetime.now(timezone.utc)

        return node_runs

    @staticmethod
    def _topological_sort(definition: PipelineDefinition):
        node_map = {node.id: node for node in definition.nodes}
        adjacency: dict[str, list[str]] = defaultdict(list)
        incoming_count: dict[str, int] = {node.id: 0 for node in definition.nodes}

        for edge in definition.edges:
            adjacency[edge.source].append(edge.target)
            incoming_count[edge.target] += 1

        queue = deque(node_id for node_id, count in incoming_count.items() if count == 0)
        ordered = []

        while queue:
            node_id = queue.popleft()
            ordered.append(node_map[node_id])

            for child in adjacency[node_id]:
                incoming_count[child] -= 1
                if incoming_count[child] == 0:
                    queue.append(child)

        return ordered

    @classmethod
    def _is_executable_node(cls, node_type: str) -> bool:
        return node_type.startswith(cls.EXECUTABLE_PREFIXES)
