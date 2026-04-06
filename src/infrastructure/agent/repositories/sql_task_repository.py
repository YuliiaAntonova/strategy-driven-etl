from __future__ import annotations

import json
import uuid
from datetime import datetime, timezone
from typing import Any

from sqlalchemy import text

from src.config.settings import settings
from src.domain.agent.contracts.task_repository import TaskRepository
from src.infrastructure.connectors.factory import get_postgres_connector
from src.infrastructure.connectors.postgres import PostgreSQLConnector


class SQLTaskRepository(TaskRepository):
    def __init__(self, connector: PostgreSQLConnector | None = None) -> None:
        self.connector = get_postgres_connector(connector)
        self._engine = self.connector.get_engine()
        self._ensure_tables()

    def _ensure_tables(self) -> None:
        create_tasks = text(f"""
        create table if not exists {settings.agent_task_table} (
            task_id varchar(36) primary key,
            prompt text not null,
            status varchar(32) not null,
            plan_json text not null,
            result_json text,
            error_text text,
            created_at timestamp not null,
            updated_at timestamp not null
        )
        """)
        create_steps = text(f"""
        create table if not exists {settings.agent_task_step_table} (
            task_id varchar(36) not null,
            step_no integer not null,
            tool_name varchar(100) not null,
            status varchar(32) not null,
            input_json text,
            output_json text,
            error_text text,
            started_at timestamp,
            finished_at timestamp,
            primary key (task_id, step_no)
        )
        """)
        with self._engine.begin() as connection:
            connection.execute(create_tasks)
            connection.execute(create_steps)

    @staticmethod
    def _utc_now() -> datetime:
        return datetime.now(timezone.utc).replace(tzinfo=None)

    @staticmethod
    def _loads(value: str | None) -> dict[str, Any] | list[dict[str, Any]] | None:
        if not value:
            return None
        return json.loads(value)

    def create_task(self, prompt: str, plan: list[dict[str, Any]]) -> str:
        task_id = str(uuid.uuid4())
        now = self._utc_now()
        with self._engine.begin() as connection:
            connection.execute(
                text(f"""
                insert into {settings.agent_task_table} (
                    task_id, prompt, status, plan_json, result_json, error_text, created_at, updated_at
                ) values (
                    :task_id, :prompt, :status, :plan_json, :result_json, :error_text, :created_at, :updated_at
                )
                """),
                {
                    "task_id": task_id,
                    "prompt": prompt,
                    "status": "pending",
                    "plan_json": json.dumps(plan),
                    "result_json": None,
                    "error_text": None,
                    "created_at": now,
                    "updated_at": now,
                },
            )
        return task_id

    def update_task_status(self, task_id: str, status: str) -> None:
        with self._engine.begin() as connection:
            connection.execute(
                text(f"update {settings.agent_task_table} set status = :status, updated_at = :updated_at where task_id = :task_id"),
                {"task_id": task_id, "status": status, "updated_at": self._utc_now()},
            )

    def complete_task(self, task_id: str, result: dict[str, Any]) -> None:
        with self._engine.begin() as connection:
            connection.execute(
                text(f"""
                update {settings.agent_task_table}
                set status = :status,
                    result_json = :result_json,
                    error_text = null,
                    updated_at = :updated_at
                where task_id = :task_id
                """),
                {
                    "task_id": task_id,
                    "status": "completed",
                    "result_json": json.dumps(result),
                    "updated_at": self._utc_now(),
                },
            )

    def fail_task(self, task_id: str, error: str) -> None:
        with self._engine.begin() as connection:
            connection.execute(
                text(f"""
                update {settings.agent_task_table}
                set status = :status,
                    error_text = :error_text,
                    updated_at = :updated_at
                where task_id = :task_id
                """),
                {
                    "task_id": task_id,
                    "status": "failed",
                    "error_text": error,
                    "updated_at": self._utc_now(),
                },
            )

    def start_step(self, task_id: str, step_no: int, tool_name: str, input_data: dict[str, Any]) -> None:
        with self._engine.begin() as connection:
            connection.execute(
                text(f"""
                insert into {settings.agent_task_step_table} (
                    task_id, step_no, tool_name, status, input_json, output_json, error_text, started_at, finished_at
                ) values (
                    :task_id, :step_no, :tool_name, :status, :input_json, :output_json, :error_text, :started_at, :finished_at
                )
                on conflict (task_id, step_no) do update set
                    tool_name = excluded.tool_name,
                    status = excluded.status,
                    input_json = excluded.input_json,
                    output_json = excluded.output_json,
                    error_text = excluded.error_text,
                    started_at = excluded.started_at,
                    finished_at = excluded.finished_at
                """),
                {
                    "task_id": task_id,
                    "step_no": step_no,
                    "tool_name": tool_name,
                    "status": "running",
                    "input_json": json.dumps(input_data),
                    "output_json": None,
                    "error_text": None,
                    "started_at": self._utc_now(),
                    "finished_at": None,
                },
            )

    def finish_step(self, task_id: str, step_no: int, output_data: dict[str, Any]) -> None:
        with self._engine.begin() as connection:
            connection.execute(
                text(f"""
                update {settings.agent_task_step_table}
                set status = :status,
                    output_json = :output_json,
                    error_text = null,
                    finished_at = :finished_at
                where task_id = :task_id and step_no = :step_no
                """),
                {
                    "task_id": task_id,
                    "step_no": step_no,
                    "status": "completed",
                    "output_json": json.dumps(output_data),
                    "finished_at": self._utc_now(),
                },
            )

    def fail_step(self, task_id: str, step_no: int, error: str) -> None:
        with self._engine.begin() as connection:
            connection.execute(
                text(f"""
                update {settings.agent_task_step_table}
                set status = :status,
                    error_text = :error_text,
                    finished_at = :finished_at
                where task_id = :task_id and step_no = :step_no
                """),
                {
                    "task_id": task_id,
                    "step_no": step_no,
                    "status": "failed",
                    "error_text": error,
                    "finished_at": self._utc_now(),
                },
            )

    def get_task(self, task_id: str) -> dict[str, Any] | None:
        with self._engine.begin() as connection:
            task_row = connection.execute(
                text(f"select * from {settings.agent_task_table} where task_id = :task_id"),
                {"task_id": task_id},
            ).mappings().first()
            if task_row is None:
                return None

            step_rows = connection.execute(
                text(f"select * from {settings.agent_task_step_table} where task_id = :task_id order by step_no"),
                {"task_id": task_id},
            ).mappings().all()

        return {
            "task_id": task_row["task_id"],
            "prompt": task_row["prompt"],
            "status": task_row["status"],
            "plan": self._loads(task_row["plan_json"]) or [],
            "result": self._loads(task_row["result_json"]) or {},
            "error": task_row["error_text"],
            "steps": [
                {
                    "step_no": row["step_no"],
                    "tool_name": row["tool_name"],
                    "status": row["status"],
                    "input_data": self._loads(row["input_json"]) or {},
                    "output_data": self._loads(row["output_json"]) or {},
                    "error": row["error_text"],
                }
                for row in step_rows
            ],
        }
