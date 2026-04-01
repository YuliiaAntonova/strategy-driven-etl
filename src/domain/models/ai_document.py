from __future__ import annotations

from dataclasses import dataclass, field


@dataclass(frozen=True)
class AIDocument:
    document_id: str
    entity_id: str
    source_type: str
    title: str
    content: str
    metadata: dict[str, str] = field(default_factory=dict)
