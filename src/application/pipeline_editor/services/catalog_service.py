from __future__ import annotations

from src.domain.pipeline_editor.models import NodeTypeDefinition
from src.domain.pipeline_editor.contracts.node_catalog import BaseNodeCatalog


class NodeCatalogService:
    """Expose node types to the UI without leaking infrastructure details."""

    def __init__(self, catalog: BaseNodeCatalog):
        self._catalog = catalog

    def list_node_types(self) -> list[NodeTypeDefinition]:
        return self._catalog.list_node_types()
