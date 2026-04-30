"""Base classes and shared helpers for Postgres SQL write strategies."""

from __future__ import annotations

from sqlalchemy import text

from src.domain.contracts.write_strategy import BaseWriteStrategy
from src.infrastructure.writing.shared.staged_sql_writer import StagedSqlTableWriter


class BasePostgresSQLWriter(StagedSqlTableWriter):
    """Postgres-specific DDL helpers on top of staged SQL writes."""

    def _rename_table(self, conn, source_table_name: str, target_table_name: str) -> None:
        conn.execute(
            text(
                f'ALTER TABLE "{source_table_name}" '
                f'RENAME TO "{target_table_name}"'
            )
        )

    def _replace_target_with_staged(self, conn) -> None:
        conn.execute(text(f'DROP TABLE IF EXISTS "{self.table_name}"'))
        self._rename_table(conn, self.temp_table_name, self.table_name)

    def _delete_duplicate_rows(self, conn, table_name: str) -> None:
        if not self.primary_key:
            return

        conn.execute(
            text(
                f'''
                DELETE FROM "{table_name}"
                WHERE ctid NOT IN (
                    SELECT MIN(ctid)
                    FROM "{table_name}"
                    GROUP BY "{self.primary_key}"
                )
                '''
            )
        )

    def _ensure_unique_index(self, conn, table_name: str) -> None:
        if not self.primary_key:
            return

        index_name = self._build_unique_index_name(table_name, self.primary_key)
        conn.execute(
            text(
                f'CREATE UNIQUE INDEX IF NOT EXISTS "{index_name}" '
                f'ON "{table_name}" ("{self.primary_key}")'
            )
        )

    def _build_unique_index_name(self, table_name: str, column_name: str) -> str:
        return f"ux_{table_name}_{column_name}"

    def _build_index_name(self, table_name: str, columns: list[str]) -> str:
        return f'ix_{table_name}_{"_".join(columns)}'


class PrimaryKeyPostgresSQLWriter(BasePostgresSQLWriter):
    """Writer base that enforces the presence of a primary key in input data."""

    def __init__(self, connector, table_name: str, primary_key: str):
        super().__init__(
            connector=connector,
            table_name=table_name,
            primary_key=primary_key,
        )

    def requires_primary_key(self) -> bool:
        return True
