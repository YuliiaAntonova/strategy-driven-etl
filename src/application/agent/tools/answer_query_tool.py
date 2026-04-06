from __future__ import annotations

from typing import Any

from src.application.agent.tools.base import AgentTool, ToolContext
from src.application.use_cases.answer_query import answer_query


class AnswerQueryTool(AgentTool):
    name = "answer_query"
    description = "Answer a user question using the indexed AI artifacts"

    def run(self, payload: dict[str, Any], context: ToolContext) -> dict[str, Any]:
        question = payload["question"]
        answer = answer_query(
            question=question,
            profile=payload.get("profile"),
            top_k=payload.get("top_k"),
        )
        return {"message": "Question answered", "question": question, "answer": answer}
