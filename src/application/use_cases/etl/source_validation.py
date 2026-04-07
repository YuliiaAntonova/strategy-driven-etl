"""Validation helpers for ETL sources."""

from __future__ import annotations

from pathlib import Path


def ensure_non_empty_file(path: Path) -> None:
    """Ensure file exists and is non-empty."""

    if not path.exists():
        raise FileNotFoundError(f"Source file does not exist: {path}")
    if path.stat().st_size == 0:
        raise ValueError(f"Source file is empty: {path}")

