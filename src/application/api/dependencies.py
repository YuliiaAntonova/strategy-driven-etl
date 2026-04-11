from __future__ import annotations

from functools import lru_cache

from src.application.agent.executor import AgentExecutor
from src.application.agent.planner import AgentPlanner
from src.application.agent.task_service import AgentTaskService
from src.application.agent.tool_registry import AgentToolRegistry
from src.application.pipeline_editor.services.catalog_service import NodeCatalogService
from src.application.pipeline_editor.services.definition_service import PipelineDefinitionService
from src.application.pipeline_editor.services.runtime_builder import PipelineRuntimeBuilder
from src.application.pipeline_editor.services.runtime_run_service import PipelineRuntimeRunService
from src.application.pipeline_editor.services.validation_service import PipelineValidationService
from src.application.pipeline_runtime.runner import VisualPipelineRunner
from src.infrastructure.agent.repositories.sql_task_repository import SQLTaskRepository
from src.infrastructure.pipeline_editor.catalog.static_node_catalog import StaticNodeCatalog
from src.infrastructure.pipeline_editor.repositories.file_pipeline_definition_repository import FilePipelineDefinitionRepository
from src.infrastructure.pipeline_editor.repositories.in_memory_pipeline_run_repository import InMemoryPipelineRunRepository
from src.infrastructure.pipeline_runtime.executors.ai_indexing_executor import AiIndexingExecutor
from src.infrastructure.pipeline_runtime.executors.etl_executor import EtlExecutor
from src.infrastructure.pipeline_runtime.executors.jobs_ingestion_executor import JobsIngestionExecutor
from src.infrastructure.pipeline_runtime.registry import NodeExecutorRegistry


@lru_cache(maxsize=1)
def get_task_repository() -> SQLTaskRepository:
    return SQLTaskRepository()


@lru_cache(maxsize=1)
def get_task_service() -> AgentTaskService:
    return AgentTaskService(task_repository=get_task_repository())


@lru_cache(maxsize=1)
def get_tool_registry() -> AgentToolRegistry:
    return AgentToolRegistry()


@lru_cache(maxsize=1)
def get_planner() -> AgentPlanner:
    return AgentPlanner()


@lru_cache(maxsize=1)
def get_executor() -> AgentExecutor:
    return AgentExecutor(tool_registry=get_tool_registry(), task_service=get_task_service())


@lru_cache(maxsize=1)
def get_pipeline_definition_repository() -> FilePipelineDefinitionRepository:
    return FilePipelineDefinitionRepository()


@lru_cache(maxsize=1)
def get_pipeline_run_repository() -> InMemoryPipelineRunRepository:
    return InMemoryPipelineRunRepository()


@lru_cache(maxsize=1)
def get_node_catalog() -> StaticNodeCatalog:
    return StaticNodeCatalog()


@lru_cache(maxsize=1)
def get_pipeline_definition_service() -> PipelineDefinitionService:
    return PipelineDefinitionService(repository=get_pipeline_definition_repository())


@lru_cache(maxsize=1)
def get_pipeline_validation_service() -> PipelineValidationService:
    return PipelineValidationService()


@lru_cache(maxsize=1)
def get_pipeline_runtime_builder() -> PipelineRuntimeBuilder:
    return PipelineRuntimeBuilder()


@lru_cache(maxsize=1)
def get_node_executor_registry() -> NodeExecutorRegistry:
    return NodeExecutorRegistry(
        executors={
            "entry.jobs_ingestion": JobsIngestionExecutor(),
            "entry.etl": EtlExecutor(),
            "entry.ai_indexing": AiIndexingExecutor(),
        }
    )


@lru_cache(maxsize=1)
def get_visual_pipeline_runner() -> VisualPipelineRunner:
    return VisualPipelineRunner(registry=get_node_executor_registry())


@lru_cache(maxsize=1)
def get_pipeline_runtime_run_service() -> PipelineRuntimeRunService:
    return PipelineRuntimeRunService(
        run_repository=get_pipeline_run_repository(),
        runner=get_visual_pipeline_runner(),
    )


@lru_cache(maxsize=1)
def get_node_catalog_service() -> NodeCatalogService:
    return NodeCatalogService(catalog=get_node_catalog())
