from __future__ import annotations

from abc import ABC, abstractmethod

from pandas import DataFrame

from src.domain.models.change_set import ChangeSet


class BaseChangeDetector(ABC):
    @abstractmethod
    def detect(self, incoming_df: DataFrame, existing_df: DataFrame) -> ChangeSet:
        raise NotImplementedError
