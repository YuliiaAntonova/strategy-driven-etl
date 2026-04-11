from __future__ import annotations

from src.domain.pipeline_runtime.executors import NodeExecutor


class NodeExecutorRegistry:
    def __init__(self, executors: dict[str, NodeExecutor]):
        self._executors = executors

    def get(self, node_type: str) -> NodeExecutor:
        executor = self._executors.get(node_type)
        if executor is None:
            raise ValueError(f"Executor is not registered for node type '{node_type}'")
        return executor
