from src.domain.contracts.load_strategy import BaseLoadStrategy
from src.infrastructure.versioning.full_load import FullLoadStrategy
from src.infrastructure.versioning.incremental_by_date import IncrementalByDateStrategy
from src.infrastructure.versioning.incremental_by_hash import IncrementalByHashStrategy
from src.infrastructure.versioning.incremental_by_primary_key import IncrementalByPrimaryKeyStrategy
from src.infrastructure.versioning.incremental_by_primary_key_and_hash import (
    IncrementalByPrimaryKeyAndHashStrategy,
)


def get_load_strategy(
    load_mode: str,
    date_column: str | None = None,
    primary_key: str | None = None,
    hash_column: str = "row_hash",
) -> BaseLoadStrategy:
    if load_mode == "full":
        return FullLoadStrategy()
    if load_mode == "incremental-by-date":
        if not date_column:
            raise ValueError("date_column is required for incremental-by-date")
        return IncrementalByDateStrategy(date_column=date_column)
    if load_mode == "incremental-by-primary-key":
        if not primary_key:
            raise ValueError("primary_key is required for incremental-by-primary-key")
        return IncrementalByPrimaryKeyStrategy(primary_key=primary_key)
    if load_mode == "incremental-by-hash":
        return IncrementalByHashStrategy(hash_column=hash_column)
    if load_mode == "incremental-by-primary-key-and-hash":
        if not primary_key:
            raise ValueError("primary_key is required for incremental-by-primary-key-and-hash")
        return IncrementalByPrimaryKeyAndHashStrategy(primary_key=primary_key, hash_column=hash_column)
    raise ValueError(f"Unsupported load_mode: {load_mode}")
