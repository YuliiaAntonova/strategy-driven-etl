from __future__ import annotations

from collections.abc import Callable

from src.application.pipeline.writer_dispatch import WRITER_FACTORIES
from src.domain.contracts.change_detector import BaseChangeDetector
from src.infrastructure.detectors.full_snapshot import FullSnapshotDetector
from src.infrastructure.detectors.incremental_by_date import IncrementalByDateDetector
from src.infrastructure.detectors.incremental_by_hash import IncrementalByHashDetector
from src.infrastructure.detectors.incremental_by_primary_key import IncrementalByPrimaryKeyDetector
from src.infrastructure.detectors.incremental_by_primary_key_and_hash import IncrementalByPrimaryKeyAndHashDetector

DetectorFactory = Callable[[str | None, str | None, str], BaseChangeDetector]


def _full_detector_factory(date_column: str | None, primary_key: str | None, hash_column: str) -> BaseChangeDetector:
    return FullSnapshotDetector(primary_key=primary_key, hash_column=hash_column)


def _incremental_by_date_detector_factory(date_column: str | None, primary_key: str | None, hash_column: str) -> BaseChangeDetector:
    if not date_column:
        raise ValueError("date_column is required for incremental-by-date")
    if not primary_key:
        raise ValueError("primary_key is required for incremental-by-date in historized mode")
    return IncrementalByDateDetector(date_column=date_column, primary_key=primary_key, hash_column=hash_column)


def _incremental_by_primary_key_detector_factory(date_column: str | None, primary_key: str | None, hash_column: str) -> BaseChangeDetector:
    if not primary_key:
        raise ValueError("primary_key is required for incremental-by-primary-key")
    return IncrementalByPrimaryKeyDetector(primary_key=primary_key, hash_column=hash_column)


def _incremental_by_hash_detector_factory(date_column: str | None, primary_key: str | None, hash_column: str) -> BaseChangeDetector:
    if not primary_key:
        raise ValueError("primary_key is required for incremental-by-hash in historized mode")
    return IncrementalByHashDetector(primary_key=primary_key, hash_column=hash_column)


def _incremental_by_primary_key_and_hash_detector_factory(date_column: str | None, primary_key: str | None, hash_column: str) -> BaseChangeDetector:
    if not primary_key:
        raise ValueError("primary_key is required for incremental-by-primary-key-and-hash")
    return IncrementalByPrimaryKeyAndHashDetector(primary_key=primary_key, hash_column=hash_column)


DETECTOR_FACTORIES: dict[str, DetectorFactory] = {
    "full": _full_detector_factory,
    "incremental-by-date": _incremental_by_date_detector_factory,
    "incremental-by-primary-key": _incremental_by_primary_key_detector_factory,
    "incremental-by-hash": _incremental_by_hash_detector_factory,
    "incremental-by-primary-key-and-hash": _incremental_by_primary_key_and_hash_detector_factory,
}

__all__ = ["DETECTOR_FACTORIES", "WRITER_FACTORIES"]
