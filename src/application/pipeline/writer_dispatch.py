from __future__ import annotations

from collections.abc import Callable

from src.domain.contracts.write_strategy import BaseWriteStrategy
from src.infrastructure.writing.append_writer import AppendWriteStrategy
from src.infrastructure.writing.replace_writer import ReplaceWriteStrategy
from src.infrastructure.writing.upsert_writer import UpsertWriteStrategy
from src.infrastructure.writing.versioned_writer import VersionedWriteStrategy
from src.infrastructure.writing.snowflake_writer import (
    SnowflakeAppendWriteStrategy,
    SnowflakeReplaceWriteStrategy,
    SnowflakeVersionedWriteStrategy,
)

WriterFactory = Callable[[object, str, str | None, str], BaseWriteStrategy]

_WRITER_CLASSES: dict[tuple[str, str], type[BaseWriteStrategy]] = {
    ("postgres", "replace"): ReplaceWriteStrategy,
    ("postgres", "append"): AppendWriteStrategy,
    ("postgres", "upsert"): UpsertWriteStrategy,
    ("postgres", "versioned"): VersionedWriteStrategy,
    ("snowflake", "replace"): SnowflakeReplaceWriteStrategy,
    ("snowflake", "append"): SnowflakeAppendWriteStrategy,
    ("snowflake", "versioned"): SnowflakeVersionedWriteStrategy,
}


def _backend_for_destination(destination_type: str) -> str:
    if destination_type == "snowflake":
        return "snowflake"
    return "postgres"


def create_writer(
    write_mode: str,
    connector: object,
    table_name: str,
    primary_key: str | None,
    destination_type: str,
) -> BaseWriteStrategy:
    if write_mode == "versioned" and not primary_key:
        raise ValueError("primary_key is required for versioned writer")

    if write_mode == "upsert" and not primary_key:
        raise ValueError("primary_key is required for upsert writer")

    backend = _backend_for_destination(destination_type)

    if write_mode == "upsert" and backend == "snowflake":
        raise ValueError("upsert is implemented for postgres only; pick another write_mode for snowflake")
    try:
        cls = _WRITER_CLASSES[(backend, write_mode)]
    except KeyError as exc:
        raise ValueError(
            f"Unsupported write_mode '{write_mode}' for backend '{backend}'"
        ) from exc

    return cls(connector=connector, table_name=table_name, primary_key=primary_key)


def _make_writer_factory(write_mode: str) -> WriterFactory:
    def factory(
        connector: object,
        table_name: str,
        primary_key: str | None,
        destination_type: str,
    ) -> BaseWriteStrategy:
        return create_writer(write_mode, connector, table_name, primary_key, destination_type)

    return factory


WRITER_FACTORIES: dict[str, WriterFactory] = {
    "replace": _make_writer_factory("replace"),
    "append": _make_writer_factory("append"),
    "upsert": _make_writer_factory("upsert"),
    "versioned": _make_writer_factory("versioned"),
}
