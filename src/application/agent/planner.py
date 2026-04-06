from __future__ import annotations

from typing import Any


class AgentPlanner:
    """Rule-based planner for the first agent integration.

    The planner converts a natural-language prompt into a safe, whitelisted plan
    built only from the project's approved use cases.
    """

    def plan(self, prompt: str, requested_profile: str | None = None) -> list[dict[str, Any]]:
        text = prompt.lower()

        if ("refresh" in text or "reload" in text) and ("index" in text or "reindex" in text):
            return [
                {"tool": "run_jobs_ingestion", "input": {}},
                {
                    "tool": "run_etl",
                    "input": {
                        "profile": requested_profile or "historized_snapshot",
                        "primary_key": "id",
                    },
                },
                {"tool": "run_ai_indexing", "input": {"profile": "jobs_rag_local"}},
            ]

        if "ingest" in text or "load raw jobs" in text or "fetch jobs" in text:
            return [{"tool": "run_jobs_ingestion", "input": {}}]

        if "historized" in text or "run etl" in text or "etl" in text:
            return [
                {
                    "tool": "run_etl",
                    "input": {
                        "profile": requested_profile or "historized_snapshot",
                        "primary_key": "id",
                    },
                }
            ]

        if "rebuild index" in text or "run ai indexing" in text or "indexing" in text:
            return [{"tool": "run_ai_indexing", "input": {"profile": requested_profile or "jobs_rag_local"}}]

        return [
            {
                "tool": "answer_query",
                "input": {
                    "question": prompt,
                    "profile": requested_profile or "jobs_rag_local",
                },
            }
        ]
