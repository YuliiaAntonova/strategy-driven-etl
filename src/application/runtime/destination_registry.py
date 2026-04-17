from __future__ import annotations

from collections.abc import Callable


class DestinationRegistry:
    def __init__(self):
        self._factories: dict[str, Callable] = {}

    def register(self, destination_type: str, factory: Callable) -> None:
        self._factories[destination_type] = factory

    def build(self, destination_spec, credentials):
        if destination_spec.type not in self._factories:
            raise ValueError(f"Unsupported destination type: {destination_spec.type}")
        return self._factories[destination_spec.type](destination_spec, credentials)
