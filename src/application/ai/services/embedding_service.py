from __future__ import annotations

import json

from pandas import DataFrame

from src.domain.contracts.embedder import BaseEmbedder


class EmbeddingService:
    def __init__(self, embedder: BaseEmbedder):
        self.embedder = embedder

    def add_embeddings(self, chunks_df: DataFrame) -> DataFrame:
        if chunks_df.empty:
            result = chunks_df.copy()
            result["embedding_json"] = []
            return result

        embeddings = self.embedder.embed(chunks_df["content"].astype(str).tolist())
        result = chunks_df.copy()
        result["embedding_json"] = [json.dumps(vector) for vector in embeddings]
        return result
