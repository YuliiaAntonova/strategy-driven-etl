from collections.abc import Callable

from src.domain.contracts.write_strategy import BaseWriteStrategy
from src.infrastructure.writing.append_writer import AppendWriteStrategy
from src.infrastructure.writing.replace_writer import ReplaceWriteStrategy
from src.infrastructure.writing.upsert_writer import UpsertWriteStrategy
from src.infrastructure.writing.versioned_writer import VersionedWriteStrategy


WRITE_MODES = ["replace", "append", "upsert", "versioned"]


WriteStrategyFactory = Callable[[object, str, str | None], BaseWriteStrategy]


def _replace_write_factory(
    connector, table_name: str, primary_key: str | None
) -> BaseWriteStrategy:
    return ReplaceWriteStrategy(
        connector=connector,
        table_name=table_name,
        primary_key=primary_key,
    )


def _append_write_factory(
    connector, table_name: str, primary_key: str | None
) -> BaseWriteStrategy:
    return AppendWriteStrategy(
        connector=connector,
        table_name=table_name,
        primary_key=primary_key,
    )


def _upsert_write_factory(
    connector, table_name: str, primary_key: str | None
) -> BaseWriteStrategy:
    if not primary_key:
        raise ValueError("primary_key is required for upsert write mode")
    return UpsertWriteStrategy(
        connector=connector,
        table_name=table_name,
        primary_key=primary_key,
    )


def _versioned_write_factory(
    connector, table_name: str, primary_key: str | None
) -> BaseWriteStrategy:
    if not primary_key:
        raise ValueError("primary_key is required for versioned write mode")
    return VersionedWriteStrategy(
        connector=connector,
        table_name=table_name,
        primary_key=primary_key,
    )


_WRITE_STRATEGY_FACTORIES: dict[str, WriteStrategyFactory] = {
    "replace": _replace_write_factory,
    "append": _append_write_factory,
    "upsert": _upsert_write_factory,
    "versioned": _versioned_write_factory,
}


def get_write_strategy(
    write_mode: str,
    connector,
    table_name: str,
    primary_key: str | None = None,
) -> BaseWriteStrategy:
    try:
        factory = _WRITE_STRATEGY_FACTORIES[write_mode]
    except KeyError:
        raise ValueError(f"Unsupported write_mode: {write_mode}") from None

    return factory(connector, table_name, primary_key)