from __future__ import annotations


def select_star_from_single_table(
    *,
    destination_type: str,
    table_name: str,
    destination_credentials: dict | None = None,
    destination_config: dict | None = None,
) -> str:
    """Return ``SELECT *`` for reading existing target rows into a DataFrame."""
    if destination_type == "bigquery":
        cfg = destination_config or {}
        ref = cfg.get("table_reference")
        if ref:
            return f"SELECT * FROM `{ref}`"

        if not destination_credentials:
            raise ValueError("bigquery requires destination credentials for state SQL")
        project_id = destination_credentials["project_id"]
        dataset_id = destination_credentials["dataset"]
        return f"SELECT * FROM `{project_id}.{dataset_id}.{table_name}`"

    escaped = table_name.replace('"', '""')
    return f'SELECT * FROM "{escaped}"'
