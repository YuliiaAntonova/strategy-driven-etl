"""Shared SQL helper utilities used by Postgres write strategies/loaders."""

from __future__ import annotations

from collections.abc import Iterable


def build_versioned_dedup_cte(
    *,
    temp_table_name: str,
    target_table_name: str,
    primary_key: str,
    only_current: bool = False,
) -> str:
    """Build a CTE that deduplicates staged rows and exposes latest target rows.

    Produces:
    - staged: deduplicated rows from the staging table (temp_table_name)
    - latest_target: the latest row per primary key from the target table

    Notes:
    - We deduplicate staged rows by primary key using Postgres DISTINCT ON.
    - If only_current=True, latest_target is filtered to current rows.
    """

    current_filter = 'WHERE "is_current" = true' if only_current else ""
    # Prefer newest by date_loaded/date_created when present, otherwise arbitrary.
    return f"""
WITH staged AS (
    SELECT DISTINCT ON (\"{primary_key}\") *
    FROM \"{temp_table_name}\"
    ORDER BY \"{primary_key}\", \"date_loaded\" DESC NULLS LAST, \"date_created\" DESC NULLS LAST
),
latest_target AS (
    SELECT DISTINCT ON (\"{primary_key}\") *
    FROM \"{target_table_name}\"
    {current_filter}
    ORDER BY \"{primary_key}\", \"date_loaded\" DESC NULLS LAST, \"date_created\" DESC NULLS LAST
)
"""



def quote_identifiers(columns: Iterable[str]) -> list[str]:
    """Return a list of column names quoted for SQL ("col")."""
    return [f'"{column}"' for column in columns]
