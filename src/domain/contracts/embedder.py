"""Domain contract for embedding text into vectors."""

from __future__ import annotations

from abc import ABC, abstractmethod


class BaseEmbedder(ABC):
    """Embedder interface (token_frequency/openai/etc.)."""

    @abstractmethod
    def embed(self, texts: list[str]) -> list[list[float]]:
        """Return embedding vectors for the given texts."""
        raise NotImplementedError
