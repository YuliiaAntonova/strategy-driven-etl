"""BigQuery DDL helpers: infer schema from pandas, create partitioned/clustered tables."""

from __future__ import annotations

from typing import TYPE_CHECKING

import pandas as pd
from google.api_core.exceptions import NotFound
from google.cloud.bigquery import SchemaField, Table, TimePartitioning

if TYPE_CHECKING:
    from google.cloud.bigquery import Client


def infer_schema_from_dataframe(df: pd.DataFrame) -> list[SchemaField]:
    fields: list[SchemaField] = []
    for column in df.columns:
        series = df[column]
        dtype = series.dtype
        if pd.api.types.is_integer_dtype(dtype):
            bq_type = "INT64"
        elif pd.api.types.is_float_dtype(dtype):
            bq_type = "FLOAT64"
        elif pd.api.types.is_bool_dtype(dtype):
            bq_type = "BOOL"
        elif pd.api.types.is_datetime64_any_dtype(dtype):
            bq_type = "TIMESTAMP"
        else:
            bq_type = "STRING"
        fields.append(SchemaField(column, bq_type, mode="NULLABLE"))
    return fields


def resolve_table_fqn(
    *,
    project_id: str,
    dataset_id: str,
    table_short: str,
    logical_table_name: str | None,
    table_reference: str | None,
) -> str:
    """Return ``project.dataset.table`` for BigQuery API (no backticks)."""
    if table_reference and logical_table_name and table_short == logical_table_name:
        parts = table_reference.split(".")
        if len(parts) != 3:
            raise ValueError(
                "table_reference must be exactly project.dataset.table (three segments)"
            )
        return ".".join(parts)
    return f"{project_id}.{dataset_id}.{table_short}"


def ensure_partitioned_table(
    client: Client,
    *,
    table_fqn: str,
    df: pd.DataFrame,
    partition_field: str | None,
    cluster_fields: list[str],
) -> None:
    """Create table if missing with optional time partitioning and clustering."""
    if not partition_field and not cluster_fields:
        return

    if partition_field and partition_field not in df.columns:
        raise ValueError(f"partition_field '{partition_field}' not found in dataframe columns")

    for column in cluster_fields:
        if column not in df.columns:
            raise ValueError(f"cluster_fields contains unknown column '{column}'")

    if partition_field:
        series = df[partition_field]
        if not pd.api.types.is_datetime64_any_dtype(series):
            raise ValueError(
                f"partition_field '{partition_field}' must be datetime64 in the dataframe "
                "(TIMESTAMP partition); coerce dtypes before load."
            )

    try:
        client.get_table(table_fqn)
        return
    except NotFound:
        pass

    schema = infer_schema_from_dataframe(df)
    table = Table(table_fqn, schema=schema)

    if partition_field:
        table.time_partitioning = TimePartitioning(field=partition_field)

    if cluster_fields:
        table.clustering_fields = list(cluster_fields)

    client.create_table(table)
