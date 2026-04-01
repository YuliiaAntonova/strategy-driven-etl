from __future__ import annotations

from collections.abc import Iterable



def quote_identifiers(columns: Iterable[str]) -> list[str]:
    """Return a list of column names quoted for SQL ("col")."""
    return [f'"{column}"' for column in columns]
