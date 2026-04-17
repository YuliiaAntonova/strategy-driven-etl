from __future__ import annotations

from collections.abc import Callable


class SourceRegistry:
    def __init__(self):
        self._factories: dict[str, Callable] = {}

    def register(self, source_type: str, factory: Callable) -> None:
        self._factories[source_type] = factory

    def build(self, source_spec, credentials):
        if source_spec.type not in self._factories:
            raise ValueError(f"Unsupported source type: {source_spec.type}")
        return self._factories[source_spec.type](source_spec, credentials)
