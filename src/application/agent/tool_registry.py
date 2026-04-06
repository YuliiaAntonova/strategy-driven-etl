from __future__ import annotations

from src.application.agent.tools.answer_query_tool import AnswerQueryTool
from src.application.agent.tools.run_ai_indexing_tool import RunAiIndexingTool
from src.application.agent.tools.run_etl_tool import RunEtlTool
from src.application.agent.tools.run_jobs_ingestion_tool import RunJobsIngestionTool


class AgentToolRegistry:
    def __init__(self) -> None:
        self._tools = {
            "run_jobs_ingestion": RunJobsIngestionTool(),
            "run_etl": RunEtlTool(),
            "run_ai_indexing": RunAiIndexingTool(),
            "answer_query": AnswerQueryTool(),
        }

    def get(self, name: str):
        try:
            return self._tools[name]
        except KeyError as exc:
            raise ValueError(f"Unknown tool: {name}") from exc

    def list_tools(self) -> list[dict[str, str]]:
        return [
            {"name": tool.name, "description": tool.description}
            for tool in self._tools.values()
        ]
