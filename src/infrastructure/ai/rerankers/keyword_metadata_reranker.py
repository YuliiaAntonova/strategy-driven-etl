"""Keyword-based reranker using metadata and content token overlap."""

from __future__ import annotations

import re

from src.domain.contracts.reranker import BaseReranker
from src.domain.models.retrieval_result import RetrievalResult


class KeywordMetadataReranker(BaseReranker):
    """Rerank results by boosting score using query overlap with metadata."""

    def rerank(
        self,
        query: str,
        results: list[RetrievalResult],
        top_k: int,
    ) -> list[RetrievalResult]:
        if not results:
            return []

        query_tokens = self._tokenize(query)
        rescored: list[RetrievalResult] = []
        for item in results:
            metadata_tokens = self._tokenize(
                " ".join(str(v) for v in item.metadata.values())
            )
            content_tokens = self._tokenize(item.content)
            title_tokens = self._tokenize(item.metadata.get("title", ""))

            metadata_boost = len(query_tokens & metadata_tokens) * 0.15
            title_boost = len(query_tokens & title_tokens) * 0.2
            content_boost = len(query_tokens & content_tokens) * 0.05
            final_score = round(
                float(item.score) + metadata_boost + title_boost + content_boost,
                6,
            )

            rescored.append(
                RetrievalResult(
                    chunk_id=item.chunk_id,
                    document_id=item.document_id,
                    entity_id=item.entity_id,
                    content=item.content,
                    score=final_score,
                    metadata=item.metadata,
                )
            )
        rescored.sort(key=lambda item: item.score, reverse=True)
        return rescored[:top_k]

    @staticmethod
    def _tokenize(text: str) -> set[str]:
        return {
            token
            for token in re.findall(r"[a-zA-Z0-9_]+", str(text).lower())
            if token
        }
