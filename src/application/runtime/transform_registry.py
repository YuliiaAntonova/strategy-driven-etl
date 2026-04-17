from __future__ import annotations

from collections.abc import Callable

from src.infrastructure.transformers.composite import CompositeTransformer
from src.infrastructure.transformers.identity import IdentityTransformer


class TransformRegistry:
    def __init__(self):
        self._factories: dict[str, Callable] = {}

    def register(self, transform_type: str, factory: Callable) -> None:
        self._factories[transform_type] = factory

    def build_chain(self, transform_specs, context):
        if not transform_specs:
            return IdentityTransformer()

        transformers = []
        for transform_spec in transform_specs:
            if transform_spec.type not in self._factories:
                raise ValueError(f"Unsupported transform type: {transform_spec.type}")
            transformers.append(self._factories[transform_spec.type](transform_spec, context))
        return CompositeTransformer(transformers=transformers)
