from __future__ import annotations

from typing import Any

from src.application.agent.tools.base import AgentTool, ToolContext
from src.application.use_cases.run_ai_indexing import run_ai_indexing


class RunAiIndexingTool(AgentTool):
    name = "run_ai_indexing"
    description = "Build AI documents, chunks, and embeddings from current records"

    def run(self, payload: dict[str, Any], context: ToolContext) -> dict[str, Any]:
        profile = payload.get("profile")
        if context.dry_run:
            return {"message": "Dry run: AI indexing would be executed", "profile": profile}

        summary = run_ai_indexing(profile=profile)
        return {
            "message": "AI indexing completed",
            **summary,
        }
