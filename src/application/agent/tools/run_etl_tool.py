from __future__ import annotations

from typing import Any

from src.application.agent.tools.base import AgentTool, ToolContext
from src.application.use_cases.run_etl import run_etl


class RunEtlTool(AgentTool):
    name = "run_etl"
    description = "Run the ETL pipeline with a supported profile or load mode"

    def run(self, payload: dict[str, Any], context: ToolContext) -> dict[str, Any]:
        resolved_profile = payload.get("profile")
        if context.dry_run:
            return {
                "message": "Dry run: ETL would be executed",
                "profile": resolved_profile,
                "load_mode": payload.get("load_mode", "full"),
            }

        run_etl(
            profile=resolved_profile,
            load_mode=payload.get("load_mode", "full"),
            write_mode=payload.get("write_mode"),
            date_column=payload.get("date_column", "date_loaded"),
            primary_key=payload.get("primary_key"),
            hash_column=payload.get("hash_column", "row_hash"),
            extract_chunk_size=payload.get("extract_chunk_size"),
            write_chunk_size=payload.get("write_chunk_size"),
        )
        result = {
            "message": "ETL completed",
            "profile": resolved_profile,
        }

        if payload.get("load_mode") is not None:
            result["load_mode"] = payload["load_mode"]

        return result

