from __future__ import annotations

from src.infrastructure.transformers.hash_columns import HashColumnsTransformer
from src.infrastructure.transformers.identity import IdentityTransformer
from src.infrastructure.transformers.jobs import JobsAuditTransformer


def build_identity_transformer(transform_spec, context):
    return IdentityTransformer()


def build_hash_columns_transformer(transform_spec, context):
    columns = transform_spec.config.get("columns")
    if not columns:
        raise ValueError("hash_columns transform requires config.columns")
    return HashColumnsTransformer(
        columns=columns,
        output_column=transform_spec.config.get("output_column", "row_hash"),
    )


def build_jobs_audit_transformer(transform_spec, context):
    return JobsAuditTransformer(
        context=context,
        source_name=transform_spec.config.get("source_name", "runtime_source"),
    )
