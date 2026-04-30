"""BigQuery connector (SQLAlchemy engine). Lazy-import dialect until ``connect()``."""

from __future__ import annotations

from src.domain.contracts.connector import BaseConnector


class BigQueryConnector(BaseConnector):
    """Snowflake-like credentials + optional destination hints (see ``bind_destination_spec``).

    Credentials::

        project_id: ${GCP_PROJECT_ID}
        dataset: ${BQ_DATASET}
        location: ${BQ_LOCATION}
        credentials_path: ${GOOGLE_APPLICATION_CREDENTIALS}

    Destination ``config`` (merged into ConnectionSpec), optional::

        table: my_table
        table_reference: my-project.analytics.my_table   # full id for target reads/MERGE
        partition_field: dt                                   # metadata hint (see bind_destination_spec)
        cluster_fields: [country, id]
        require_existing_table: true                         # pre-created DDL only; replace → TRUNCATE + append

    With ``partition_field`` / ``cluster_fields`` and ``require_existing_table: false``,
    the pipeline creates the table on first batch if it does not exist; writes use
    TRUNCATE + append for replace so partitioning/clustering are preserved.

    If ``credentials_path`` is omitted, Application Default Credentials are used.
    """

    def __init__(
        self,
        *,
        project_id: str,
        dataset: str,
        credentials_path: str | None = None,
        location: str | None = None,
    ):
        self.project_id = project_id
        self.dataset_id = dataset
        self.credentials_path = credentials_path
        self.location = location
        self._engine = None

        self.logical_table_name: str | None = None
        self.table_reference: str | None = None
        self.partition_field: str | None = None
        self.cluster_fields: list[str] = []
        self.require_existing_table: bool = False
        self._bq_client = None
        self._ddl_ensured: bool = False

    def bind_destination_spec(self, config: dict) -> None:
        """Called by ``BigQueryConnectorFactory.create_loader`` with merged destination config."""
        self.logical_table_name = config.get("table")
        self.table_reference = config.get("table_reference")
        self.partition_field = config.get("partition_field")
        self.cluster_fields = list(config.get("cluster_fields") or [])
        self.require_existing_table = bool(config.get("require_existing_table", False))

    def uses_managed_ddl(self) -> bool:
        return bool(self.partition_field or self.cluster_fields)

    def bq_client(self):
        """Native BigQuery client for DDL (same auth shape as SQLAlchemy URL)."""
        if self._bq_client is None:
            try:
                from google.cloud import bigquery
            except ImportError as exc:
                raise RuntimeError(
                    "BigQuery DDL requires google-cloud-bigquery. pip install '.[bigquery]'"
                ) from exc

            if self.credentials_path:
                from google.oauth2 import service_account

                creds = service_account.Credentials.from_service_account_file(
                    self.credentials_path
                )
                self._bq_client = bigquery.Client(project=self.project_id, credentials=creds)
            else:
                self._bq_client = bigquery.Client(project=self.project_id)
        return self._bq_client

    def ensure_target_table(self, df, logical_short: str) -> None:
        """Create partitioned/clustered table via API when configured and table is missing."""
        if self.require_existing_table:
            return
        if not self.uses_managed_ddl():
            return
        if self._ddl_ensured:
            return

        from src.infrastructure.writing.bigquery.bigquery_ddl import (
            ensure_partitioned_table,
            resolve_table_fqn,
        )

        fqn = resolve_table_fqn(
            project_id=self.project_id,
            dataset_id=self.dataset_id,
            table_short=logical_short,
            logical_table_name=self.logical_table_name,
            table_reference=self.table_reference,
        )
        ensure_partitioned_table(
            self.bq_client(),
            table_fqn=fqn,
            df=df,
            partition_field=self.partition_field,
            cluster_fields=self.cluster_fields,
        )
        self._ddl_ensured = True

    def qualified_table(self, short_name: str) -> str:
        """Fully qualified `` `...` `` id. Target row uses ``table_reference`` when it matches logical ``table``."""
        if (
            self.table_reference
            and self.logical_table_name
            and short_name == self.logical_table_name
        ):
            return f"`{self.table_reference}`"
        return f"`{self.project_id}.{self.dataset_id}.{short_name}`"

    def connect(self):
        if self._engine is None:
            try:
                from sqlalchemy import create_engine
            except ImportError as exc:
                raise RuntimeError(
                    "BigQuery requires SQLAlchemy. Install extras: pip install '.[bigquery]'"
                ) from exc

            url = f"bigquery://{self.project_id}/{self.dataset_id}"
            if self.credentials_path:
                self._engine = create_engine(url, credentials_path=self.credentials_path)
            else:
                self._engine = create_engine(url)
        return self._engine
