"""Domain contract for detecting changes between incoming and existing data."""

from __future__ import annotations

from abc import ABC, abstractmethod

from pandas import DataFrame

from src.domain.models.change_set import ChangeSet


class BaseChangeDetector(ABC):
    """Change detector interface used by the pipeline."""

    @abstractmethod
    def detect(self, incoming_df: DataFrame, existing_df: DataFrame) -> ChangeSet:
        """Return a ChangeSet describing new/changed/unchanged rows."""
        raise NotImplementedError
