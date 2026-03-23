from src.domain.contracts.write_strategy import BaseWriteStrategy
from src.infrastructure.writing.append_writer import AppendWriteStrategy
from src.infrastructure.writing.replace_writer import ReplaceWriteStrategy
from src.infrastructure.writing.upsert_writer import UpsertWriteStrategy
from src.infrastructure.writing.versioned_writer import VersionedWriteStrategy


WRITE_MODES = ["replace", "append", "upsert", "versioned"]


def get_write_strategy(
    write_mode: str,
    connector,
    table_name: str,
    primary_key: str | None = None,
) -> BaseWriteStrategy:
    if write_mode == "replace":
        return ReplaceWriteStrategy(connector=connector, table_name=table_name)
    if write_mode == "append":
        return AppendWriteStrategy(connector=connector, table_name=table_name)
    if write_mode == "upsert":
        if not primary_key:
            raise ValueError("primary_key is required for upsert write mode")
        return UpsertWriteStrategy(connector=connector, table_name=table_name, primary_key=primary_key)
    if write_mode == "versioned":
        if not primary_key:
            raise ValueError("primary_key is required for versioned write mode")
        return VersionedWriteStrategy(connector=connector, table_name=table_name, primary_key=primary_key)
    raise ValueError(f"Unsupported write_mode: {write_mode}")
