from __future__ import annotations

import json
from typing import Iterable

import pandas as pd
from pandas import DataFrame

from src.domain.models.ai_document import AIDocument


class DocumentService:
    def __init__(self, content_columns: list[str], metadata_columns: list[str]):
        self.content_columns = content_columns
        self.metadata_columns = metadata_columns

    def build_from_jobs(self, jobs_df: DataFrame) -> DataFrame:
        documents: list[dict[str, str]] = []
        if jobs_df.empty:
            return pd.DataFrame(columns=[
                "document_id", "entity_id", "source_type", "title", "content", "metadata_json"
            ])

        for _, row in jobs_df.iterrows():
            entity_id = str(row.get("id", ""))
            metadata = {
                column: self._safe_str(row.get(column, ""))
                for column in self.metadata_columns
                if column in jobs_df.columns
            }
            title = self._safe_str(row.get("title", entity_id))
            content = self._build_content(row, jobs_df.columns)
            document = AIDocument(
                document_id=entity_id,
                entity_id=entity_id,
                source_type="job",
                title=title,
                content=content,
                metadata=metadata,
            )
            documents.append({
                "document_id": document.document_id,
                "entity_id": document.entity_id,
                "source_type": document.source_type,
                "title": document.title,
                "content": document.content,
                "metadata_json": json.dumps(document.metadata, ensure_ascii=False),
            })

        return pd.DataFrame(documents)

    def _build_content(self, row, available_columns: Iterable[str]) -> str:
        sections: list[str] = []
        available = set(available_columns)
        for column in self.content_columns:
            if column not in available:
                continue
            value = self._safe_str(row.get(column, ""))
            if not value:
                continue
            label = column.replace("_", " ").title()
            sections.append(f"{label}: {value}")
        return "\n".join(sections)

    @staticmethod
    def _safe_str(value) -> str:
        if value is None:
            return ""
        if isinstance(value, float) and pd.isna(value):
            return ""
        return str(value).strip()
