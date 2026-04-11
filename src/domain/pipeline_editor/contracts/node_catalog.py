from __future__ import annotations

from abc import ABC, abstractmethod

from src.domain.pipeline_editor.models import NodeTypeDefinition


class BaseNodeCatalog(ABC):
    """Read-only catalog of node types available to the visual editor."""

    @abstractmethod
    def list_node_types(self) -> list[NodeTypeDefinition]:
        """Return all available node type definitions."""
