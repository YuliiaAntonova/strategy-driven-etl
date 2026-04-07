"""Configuration object for the `run_etl` use case.

The CLI entrypoint passes multiple flags; grouping them into a single config keeps
`run_etl` small and easier to test.
"""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class RunEtlConfig:
    """Runtime configuration for an ETL run."""

    load_mode: str = "full"
    write_mode: str | None = None
    date_column: str = "date_loaded"
    primary_key: str | None = None
    hash_column: str = "row_hash"
    extract_chunk_size: int | None = None
    write_chunk_size: int | None = None
    profile: str | None = None

    def ensure_primary_key_if_required(
        self,
        *,
        requires_primary_key: bool,
        profile_name: str,
    ) -> None:
        """Raise a ValueError if a primary key is required but missing."""
        if requires_primary_key and not self.primary_key:
            raise ValueError(f"Profile '{profile_name}' requires --primary-key")
