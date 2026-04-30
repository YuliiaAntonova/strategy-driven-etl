from __future__ import annotations


def select_star_from_single_table(*, destination_type: str, table_name: str) -> str:
    """Return ``SELECT *`` for a single quoted table identifier.

    ``destination_type`` is part of the API so dialect-specific branches (Postgres vs Snowflake,
    schema-qualified names, etc.) can be added without changing call sites.
    """
    escaped = table_name.replace('"', '""')
    _ = destination_type  # dialect hook
    return f'SELECT * FROM "{escaped}"'
