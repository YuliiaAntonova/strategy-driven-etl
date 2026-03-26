from __future__ import annotations

from collections.abc import Iterable


def quote_identifiers(columns: Iterable[str]) -> list[str]:
    """Return a list of column names quoted for SQL ("col")."""
    return [f'"{column}"' for column in columns]


def build_versioned_dedup_cte(
    temp_table_name: str,
    target_table_name: str,
    primary_key: str,
    only_current: bool = True,
) -> str:
    """Build common CTE for staged/latest_target versioned deduplication.

    Returns a SQL snippet starting with WITH staged AS (...), latest_target AS (...).
    """

    where_clause = (
        f'WHERE target."is_current" = true\n'
        if only_current
        else ""
    )

    return f'''
            WITH staged AS (
                SELECT *
                FROM (
                    SELECT
                        staged_source.*,
                        ROW_NUMBER() OVER (
                            PARTITION BY staged_source."{primary_key}"
                            ORDER BY staged_source."date_loaded" DESC NULLS LAST
                        ) AS row_number_rank
                    FROM "{temp_table_name}" staged_source
                ) ranked_stage
                WHERE ranked_stage.row_number_rank = 1
            ),
            latest_target AS (
                SELECT DISTINCT ON (target."{primary_key}")
                    target.*
                FROM "{target_table_name}" target
{where_clause}                ORDER BY target."{primary_key}", target."date_loaded" DESC NULLS LAST
            )
        '''
