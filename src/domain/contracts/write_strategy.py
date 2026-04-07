"""Domain contract for writing dataframes (or ChangeSet) into a target."""

from __future__ import annotations

from abc import ABC, abstractmethod

from pandas import DataFrame

from src.domain.models.change_set import ChangeSet


class BaseWriteStrategy(ABC):
    """Write strategy interface (append/replace/upsert/versioned, etc.)."""

    @abstractmethod
    def write(
        self,
        df: DataFrame | ChangeSet,
        chunk_size: int | None = None,
    ) -> None:
        """Write the given dataframe (or ChangeSet) to the target system."""
        raise NotImplementedError
