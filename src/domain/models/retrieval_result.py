from __future__ import annotations

from dataclasses import dataclass, field


@dataclass(frozen=True)
class RetrievalResult:
    chunk_id: str
    document_id: str
    entity_id: str
    content: str
    score: float
    metadata: dict[str, str] = field(default_factory=dict)
