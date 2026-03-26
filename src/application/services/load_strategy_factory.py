from collections.abc import Callable

from src.domain.contracts.load_strategy import BaseLoadStrategy
from src.infrastructure.versioning.full_load import FullLoadStrategy
from src.infrastructure.versioning.incremental_by_date import IncrementalByDateStrategy
from src.infrastructure.versioning.incremental_by_hash import IncrementalByHashStrategy
from src.infrastructure.versioning.incremental_by_primary_key import IncrementalByPrimaryKeyStrategy
from src.infrastructure.versioning.incremental_by_primary_key_and_hash import (
    IncrementalByPrimaryKeyAndHashStrategy,
)


LoadStrategyFactory = Callable[[str | None, str | None, str], BaseLoadStrategy]


def _full_load_factory(
    date_column: str | None, primary_key: str | None, hash_column: str
) -> BaseLoadStrategy:
    return FullLoadStrategy()


def _incremental_by_date_factory(
    date_column: str | None, primary_key: str | None, hash_column: str
) -> BaseLoadStrategy:
    if not date_column:
        raise ValueError("date_column is required for incremental-by-date")
    return IncrementalByDateStrategy(date_column=date_column)


def _incremental_by_primary_key_factory(
    date_column: str | None, primary_key: str | None, hash_column: str
) -> BaseLoadStrategy:
    if not primary_key:
        raise ValueError("primary_key is required for incremental-by-primary-key")
    return IncrementalByPrimaryKeyStrategy(primary_key=primary_key)


def _incremental_by_hash_factory(
    date_column: str | None, primary_key: str | None, hash_column: str
) -> BaseLoadStrategy:
    return IncrementalByHashStrategy(hash_column=hash_column)


def _incremental_by_primary_key_and_hash_factory(
    date_column: str | None, primary_key: str | None, hash_column: str
) -> BaseLoadStrategy:
    if not primary_key:
        raise ValueError("primary_key is required for incremental-by-primary-key-and-hash")
    return IncrementalByPrimaryKeyAndHashStrategy(
        primary_key=primary_key,
        hash_column=hash_column,
    )


_LOAD_STRATEGY_FACTORIES: dict[str, LoadStrategyFactory] = {
    "full": _full_load_factory,
    "incremental-by-date": _incremental_by_date_factory,
    "incremental-by-primary-key": _incremental_by_primary_key_factory,
    "incremental-by-hash": _incremental_by_hash_factory,
    "incremental-by-primary-key-and-hash": _incremental_by_primary_key_and_hash_factory,
}


def get_load_strategy(
    load_mode: str,
    date_column: str | None = None,
    primary_key: str | None = None,
    hash_column: str = "row_hash",
) -> BaseLoadStrategy:
    try:
        factory = _LOAD_STRATEGY_FACTORIES[load_mode]
    except KeyError:
        raise ValueError(f"Unsupported load_mode: {load_mode}") from None

    return factory(date_column, primary_key, hash_column)
