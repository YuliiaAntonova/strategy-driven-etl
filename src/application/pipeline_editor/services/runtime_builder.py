from __future__ import annotations

from collections import defaultdict, deque

from src.domain.pipeline_editor.models import BuildPlanStep, PipelineDefinition, PipelineExecutionPlan


class PipelineRuntimeBuilder:
    """Build a runtime-friendly execution plan from the visual graph."""

    def build_plan(self, definition: PipelineDefinition) -> PipelineExecutionPlan:
        adjacency: dict[str, list[str]] = defaultdict(list)
        incoming_count: dict[str, int] = {node.id: 0 for node in definition.nodes}
        node_map = {node.id: node for node in definition.nodes}

        for edge in definition.edges:
            adjacency[edge.source].append(edge.target)
            incoming_count[edge.target] += 1

        queue = deque(node_id for node_id, count in incoming_count.items() if count == 0)
        steps: list[BuildPlanStep] = []

        while queue:
            node_id = queue.popleft()
            node = node_map[node_id]
            dependencies = [edge.source for edge in definition.edges if edge.target == node_id]
            steps.append(
                BuildPlanStep(
                    node_id=node.id,
                    node_type=node.type,
                    action=f"Execute {node.type}",
                    dependencies=dependencies,
                )
            )
            for child in adjacency[node_id]:
                incoming_count[child] -= 1
                if incoming_count[child] == 0:
                    queue.append(child)

        return PipelineExecutionPlan(pipeline_id=definition.id, steps=steps)
