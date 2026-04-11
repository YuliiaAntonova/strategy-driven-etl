from __future__ import annotations

from collections import defaultdict, deque

from src.domain.pipeline_editor.models import PipelineDefinition, PipelineValidationResult, ValidationIssue, ValidationSeverity


class PipelineValidationService:
    """Validate the editable graph separately from runtime execution."""

    def validate(self, definition: PipelineDefinition) -> PipelineValidationResult:
        issues: list[ValidationIssue] = []
        node_ids = {node.id for node in definition.nodes}
        incoming_count: dict[str, int] = defaultdict(int)
        adjacency: dict[str, list[str]] = defaultdict(list)

        if not definition.nodes:
            issues.append(
                ValidationIssue(
                    code="EMPTY_PIPELINE",
                    message="Pipeline must contain at least one node.",
                    severity=ValidationSeverity.ERROR,
                )
            )

        for edge in definition.edges:
            if edge.source not in node_ids:
                issues.append(
                    ValidationIssue(
                        code="UNKNOWN_EDGE_SOURCE",
                        message=f"Edge source '{edge.source}' does not exist.",
                        severity=ValidationSeverity.ERROR,
                        edge=edge,
                    )
                )
                continue
            if edge.target not in node_ids:
                issues.append(
                    ValidationIssue(
                        code="UNKNOWN_EDGE_TARGET",
                        message=f"Edge target '{edge.target}' does not exist.",
                        severity=ValidationSeverity.ERROR,
                        edge=edge,
                    )
                )
                continue
            adjacency[edge.source].append(edge.target)
            incoming_count[edge.target] += 1

        node_type_by_id = {node.id: node.type for node in definition.nodes}

        for node in definition.nodes:
            if not node.type.strip():
                issues.append(
                    ValidationIssue(
                        code="MISSING_NODE_TYPE",
                        message="Node type is required.",
                        severity=ValidationSeverity.ERROR,
                        node_id=node.id,
                    )
                )
            if not node.name.strip():
                issues.append(
                    ValidationIssue(
                        code="MISSING_NODE_NAME",
                        message="Node name is required.",
                        severity=ValidationSeverity.ERROR,
                        node_id=node.id,
                    )
                )

            if node.type == "entry.etl":
                extractor_node_id = node.config.get("extractor_node_id")
                loader_node_id = node.config.get("loader_node_id")

                if not extractor_node_id:
                    issues.append(
                        ValidationIssue(
                            code="MISSING_ETL_EXTRACTOR",
                            message="ETL node must reference an extractor node.",
                            severity=ValidationSeverity.ERROR,
                            node_id=node.id,
                        )
                    )
                elif not str(node_type_by_id.get(str(extractor_node_id), "")).startswith("extractor."):
                    issues.append(
                        ValidationIssue(
                            code="INVALID_ETL_EXTRACTOR",
                            message="ETL node extractor reference must point to an extractor node.",
                            severity=ValidationSeverity.ERROR,
                            node_id=node.id,
                        )
                    )

                if not loader_node_id:
                    issues.append(
                        ValidationIssue(
                            code="MISSING_ETL_LOADER",
                            message="ETL node must reference a loader node.",
                            severity=ValidationSeverity.ERROR,
                            node_id=node.id,
                        )
                    )
                elif not str(node_type_by_id.get(str(loader_node_id), "")).startswith("loader."):
                    issues.append(
                        ValidationIssue(
                            code="INVALID_ETL_LOADER",
                            message="ETL node loader reference must point to a loader node.",
                            severity=ValidationSeverity.ERROR,
                            node_id=node.id,
                        )
                    )

        if definition.nodes:
            roots = [node.id for node in definition.nodes if incoming_count[node.id] == 0]
            if not roots:
                issues.append(
                    ValidationIssue(
                        code="NO_ROOT_NODE",
                        message="Pipeline graph must have at least one root node.",
                        severity=ValidationSeverity.ERROR,
                    )
                )

            ordered = self._topological_sort(node_ids=node_ids, incoming_count=incoming_count, adjacency=adjacency)
            if len(ordered) != len(node_ids):
                issues.append(
                    ValidationIssue(
                        code="CYCLE_DETECTED",
                        message="Pipeline graph contains a cycle.",
                        severity=ValidationSeverity.ERROR,
                    )
                )

        return PipelineValidationResult(valid=not any(i.severity == ValidationSeverity.ERROR for i in issues), issues=issues)

    @staticmethod
    def _topological_sort(
        *,
        node_ids: set[str],
        incoming_count: dict[str, int],
        adjacency: dict[str, list[str]],
    ) -> list[str]:
        queue = deque(node_id for node_id in node_ids if incoming_count[node_id] == 0)
        visited: list[str] = []
        remaining = dict(incoming_count)

        while queue:
            node_id = queue.popleft()
            visited.append(node_id)
            for child in adjacency[node_id]:
                remaining[child] -= 1
                if remaining[child] == 0:
                    queue.append(child)

        return visited
