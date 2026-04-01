from __future__ import annotations

import json
import re

from pandas import DataFrame

from src.domain.contracts.retriever import BaseRetriever
from src.domain.models.retrieval_result import RetrievalResult


class KeywordRetriever(BaseRetriever):
    def retrieve(self, query: str, chunks_df: DataFrame, top_k: int) -> list[RetrievalResult]:
        if chunks_df.empty:
            return []

        query_tokens = self._tokenize(query)
        scored: list[RetrievalResult] = []
        for _, row in chunks_df.iterrows():
            content = str(row.get("content", ""))
            content_tokens = self._tokenize(content)
            score = self._score(query_tokens, content_tokens)
            if score <= 0:
                continue
            metadata = json.loads(row.get("metadata_json", "{}") or "{}")
            scored.append(
                RetrievalResult(
                    chunk_id=str(row["chunk_id"]),
                    document_id=str(row["document_id"]),
                    entity_id=str(row["entity_id"]),
                    content=content,
                    score=score,
                    metadata=metadata,
                )
            )
        scored.sort(key=lambda item: item.score, reverse=True)
        return scored[:top_k]

    @staticmethod
    def _tokenize(text: str) -> set[str]:
        return {token for token in re.findall(r"[a-zA-Z0-9_]+", text.lower()) if token}

    @staticmethod
    def _score(query_tokens: set[str], content_tokens: set[str]) -> float:
        if not query_tokens or not content_tokens:
            return 0.0
        overlap = query_tokens & content_tokens
        if not overlap:
            return 0.0
        return round(len(overlap) / len(query_tokens), 6)
