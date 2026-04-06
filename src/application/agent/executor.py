from __future__ import annotations

from typing import Any

from src.application.agent.task_service import AgentTaskService
from src.application.agent.tool_registry import AgentToolRegistry
from src.application.agent.tools.base import ToolContext


class AgentExecutor:
    def __init__(self, tool_registry: AgentToolRegistry, task_service: AgentTaskService) -> None:
        self.tool_registry = tool_registry
        self.task_service = task_service

    def execute_plan(self, task_id: str, plan: list[dict[str, Any]], dry_run: bool = False) -> dict[str, Any]:
        self.task_service.mark_running(task_id)
        context = ToolContext(task_id=task_id, dry_run=dry_run)
        final_result: dict[str, Any] = {}

        for step_no, step in enumerate(plan, start=1):
            tool_name = step["tool"]
            input_data = step.get("input", {})
            self.task_service.start_step(task_id=task_id, step_no=step_no, tool_name=tool_name, input_data=input_data)

            try:
                tool = self.tool_registry.get(tool_name)
                output = tool.run(payload=input_data, context=context)
                final_result[tool_name] = output
                self.task_service.finish_step(task_id=task_id, step_no=step_no, output_data=output)
            except Exception as exc:
                error_text = str(exc)
                self.task_service.fail_step(task_id=task_id, step_no=step_no, error=error_text)
                self.task_service.mark_failed(task_id=task_id, error=error_text)
                raise

        self.task_service.mark_completed(task_id=task_id, result=final_result)
        return final_result
