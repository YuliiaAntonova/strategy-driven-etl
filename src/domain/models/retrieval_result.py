"""Domain model representing a single retrieved chunk for RAG-style flows."""

from __future__ import annotations

from dataclasses import dataclass, field


@dataclass(frozen=True)
class RetrievalResult:
    """A retrieved chunk with relevance score and optional metadata."""

    chunk_id: str
    document_id: str
    entity_id: str
    content: str
    score: float
    metadata: dict[str, str] = field(default_factory=dict)
