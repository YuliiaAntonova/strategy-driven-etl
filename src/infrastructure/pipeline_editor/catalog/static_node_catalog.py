from __future__ import annotations

from src.domain.pipeline_editor.contracts.node_catalog import BaseNodeCatalog
from src.domain.pipeline_editor.models import NodeConfigField, NodeTypeDefinition


class StaticNodeCatalog(BaseNodeCatalog):
    """Catalog that describes node types available to the future React editor."""

    def list_node_types(self) -> list[NodeTypeDefinition]:
        return [
            NodeTypeDefinition(
                type="entry.jobs_ingestion",
                label="Jobs Ingestion",
                category="Entry Points",
                description="Fetch jobs from API and save them into the source CSV.",
                config_fields=[
                    NodeConfigField(name="dataset", type="string", required=False, default="jobs"),
                    NodeConfigField(name="dt", type="string", required=False),
                    NodeConfigField(name="run_id", type="string", required=False),
                ],
            ),
            NodeTypeDefinition(
                type="entry.etl",
                label="ETL Pipeline",
                category="Entry Points",
                description="Run the main ETL pipeline from source CSV into the target store.",
                config_fields=[
                    NodeConfigField(
                        name="extractor_node_id",
                        type="extractor_ref",
                        required=True,
                        description="Extractor node used as the ETL source.",
                    ),
                    NodeConfigField(
                        name="loader_node_id",
                        type="loader_ref",
                        required=True,
                        description="Loader node used as the ETL destination.",
                    ),
                    NodeConfigField(
                        name="load_mode",
                        type="string",
                        required=False,
                        default="full",
                        options=["full", "incremental-by-date", "incremental-by-primary-key", "incremental-by-hash", "incremental-by-primary-key-and-hash"],
                    ),
                    NodeConfigField(
                        name="write_mode",
                        type="string",
                        required=False,
                        options=["replace", "append", "versioned"],
                    ),
                    NodeConfigField(name="date_column", type="string", required=False, default="date_loaded"),
                    NodeConfigField(name="primary_key", type="string", required=False),
                    NodeConfigField(name="hash_column", type="string", required=False, default="row_hash"),
                    NodeConfigField(name="extract_chunk_size", type="integer", required=False),
                    NodeConfigField(name="write_chunk_size", type="integer", required=False),
                    NodeConfigField(name="profile", type="string", required=False),
                ],
            ),
            NodeTypeDefinition(
                type="entry.ai_indexing",
                label="AI Indexing",
                category="Entry Points",
                description="Run document chunking and embeddings indexing.",
                config_fields=[
                    NodeConfigField(name="profile", type="string", required=False),
                ],
            ),
            NodeTypeDefinition(
                type="extractor.csv",
                label="CSV Extractor",
                category="Extractors",
                description="Read rows from a CSV file.",
                config_fields=[
                    NodeConfigField(name="file_path", type="string", required=True, description="Path to the source CSV file."),
                ],
            ),
            NodeTypeDefinition(
                type="transformer.jobs_audit",
                label="Jobs Audit Transformer",
                category="Transformers",
                description="Normalize job records and add ETL audit fields.",
            ),
            NodeTypeDefinition(
                type="transformer.hash_columns",
                label="Hash Columns Transformer",
                category="Transformers",
                description="Compute stable row hashes for change detection.",
                config_fields=[
                    NodeConfigField(name="columns", type="string[]", required=True, description="Columns used to build the row hash."),
                    NodeConfigField(name="output_column", type="string", required=False, default="row_hash"),
                ],
            ),
            NodeTypeDefinition(
                type="detector.incremental_by_hash",
                label="Incremental By Hash",
                category="Detectors",
                description="Detect inserts, updates, and deletes using a row hash.",
            ),
            NodeTypeDefinition(
                type="loader.postgres",
                label="Postgres Loader",
                category="Loaders",
                description="Write the result into PostgreSQL.",
                config_fields=[
                    NodeConfigField(name="table", type="string", required=True, description="Destination table name."),
                ],
            ),
            NodeTypeDefinition(
                type="ai.index_documents",
                label="Index Documents",
                category="AI",
                description="Create embeddings and push documents into the retrieval store.",
            ),
        ]
