"""Domain model representing a chunk extracted from a document."""

from __future__ import annotations

from dataclasses import dataclass, field


@dataclass(frozen=True)
class Chunk:
    """A single chunk of content associated with a document/entity."""

    chunk_id: str
    document_id: str
    entity_id: str
    position: int
    content: str
    metadata: dict[str, str] = field(default_factory=dict)
