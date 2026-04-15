from __future__ import annotations

from functools import lru_cache

from src.application.agent.executor import AgentExecutor
from src.application.agent.planner import AgentPlanner
from src.application.agent.task_service import AgentTaskService
from src.application.agent.tool_registry import AgentToolRegistry
from src.infrastructure.agent.repositories.sql_task_repository import SQLTaskRepository


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
