from __future__ import annotations

import pandas as pd
from pandas import DataFrame

from src.domain.contracts.ai_repository import BaseAIRepository
from src.infrastructure.connectors.postgres import PostgreSQLConnector


class PostgresAIRepository(BaseAIRepository):
    def __init__(self, connector: PostgreSQLConnector, document_table: str, chunk_table: str):
        self.connector = connector
        self.document_table = document_table
        self.chunk_table = chunk_table

    def replace_documents(self, documents_df: DataFrame) -> None:
        documents_df.to_sql(
            name=self.document_table,
            con=self.connector.connect(),
            if_exists="replace",
            index=False,
        )

    def replace_chunks(self, chunks_df: DataFrame) -> None:
        chunks_df.to_sql(
            name=self.chunk_table,
            con=self.connector.connect(),
            if_exists="replace",
            index=False,
        )

    def read_chunks(self) -> DataFrame:
        try:
            return pd.read_sql(f"select * from {self.chunk_table}", con=self.connector.connect())
        except Exception:
            return pd.DataFrame(columns=[
                "chunk_id", "document_id", "entity_id", "position", "content", "metadata_json", "embedding_json"
            ])
