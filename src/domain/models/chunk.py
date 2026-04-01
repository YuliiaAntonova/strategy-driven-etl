from __future__ import annotations

from dataclasses import dataclass, field


@dataclass(frozen=True)
class Chunk:
    chunk_id: str
    document_id: str
    entity_id: str
    position: int
    content: str
    metadata: dict[str, str] = field(default_factory=dict)
