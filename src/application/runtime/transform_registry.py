from __future__ import annotations

from collections.abc import Callable

from src.application.runtime.keyed_registry import KeyedRegistry
from src.infrastructure.transformers.composite import CompositeTransformer
from src.infrastructure.transformers.identity import IdentityTransformer


class TransformRegistry(KeyedRegistry[Callable]):
    def __init__(self) -> None:
        super().__init__(entity_label="transform type")

    def build_chain(self, transform_specs, context):
        if not transform_specs:
            return IdentityTransformer()

        transformers = []
        for transform_spec in transform_specs:
            factory = self.require(transform_spec.type)
            transformers.append(factory(transform_spec, context))
        return CompositeTransformer(transformers=transformers)
