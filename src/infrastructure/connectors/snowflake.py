"""Snowflake connector.

This ETL-only template does not ship Snowflake support by default.

If you need Snowflake later, re-introduce a real implementation here and add
the appropriate dependency (for example `snowflake-connector-python`).
"""

from __future__ import annotations


class SnowflakeConnector:  # pragma: no cover
    def __init__(self, *args, **kwargs):
        raise ImportError(
            "Snowflake support is not included in this ETL-only project. "
            "Add the Snowflake dependency and implement SnowflakeConnector."
        )
