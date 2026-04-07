"""Simple embedder based on token frequency hashing.

This is a lightweight, dependency-free embedder intended for demos and local
testing. It maps tokens into a fixed-size vector using hashing.
"""

from __future__ import annotations

import hashlib
import re

from src.domain.contracts.embedder import BaseEmbedder


class TokenFrequencyEmbedder(BaseEmbedder):
    """Embed text into a fixed-length vector using hashed token counts."""

    def __init__(self, dimensions: int = 64):
        self.dimensions = dimensions

    def embed(self, texts: list[str]) -> list[list[float]]:
        return [self._embed_one(text) for text in texts]

    def _embed_one(self, text: str) -> list[float]:
        vector = [0.0] * self.dimensions
        tokens = re.findall(r"[a-zA-Z0-9_]+", text.lower())
        if not tokens:
            return vector
        for token in tokens:
            bucket = (
                int(hashlib.md5(token.encode("utf-8")).hexdigest(), 16)
                % self.dimensions
            )
            vector[bucket] += 1.0
        scale = sum(abs(value) for value in vector) or 1.0
        return [round(value / scale, 6) for value in vector]
