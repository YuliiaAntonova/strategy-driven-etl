from __future__ import annotations

from typing import Generic, TypeVar

T = TypeVar("T")


class KeyedRegistry(Generic[T]):
    """Registers keyed factories or callables; unified lookup errors."""

    def __init__(self, *, entity_label: str) -> None:
        self._entity_label = entity_label
        self._entries: dict[str, T] = {}

    def register(self, key: str, item: T) -> None:
        self._entries[key] = item

    def require(self, key: str) -> T:
        try:
            return self._entries[key]
        except KeyError as exc:
            supported = ", ".join(sorted(self._entries))
            raise ValueError(
                f"Unsupported {self._entity_label} '{key}'. Supported: {supported}"
            ) from exc
