from __future__ import annotations

from src.infrastructure.transformers.factories import (
    build_hash_columns_transformer,
    build_identity_transformer,
    build_jobs_audit_transformer,
)

TRANSFORM_FACTORIES = {
    "identity": build_identity_transformer,
    "jobs_audit": build_jobs_audit_transformer,
    "hash_columns": build_hash_columns_transformer,
}
