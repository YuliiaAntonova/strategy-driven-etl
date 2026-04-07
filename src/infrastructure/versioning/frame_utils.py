"""Utilities for "versioned" (historized snapshot) pandas DataFrames.

These helpers normalize timestamp columns, filter existing frames to the
current version, and prepare new/changed rows for historized loading.
"""

from __future__ import annotations

import pandas as pd
from pandas import DataFrame


def _normalize_versioned_dates(df: DataFrame) -> DataFrame:
    """Coerce common versioning timestamp columns to UTC datetimes."""
    normalized = df.copy()
    normalized["date_created"] = pd.to_datetime(
        normalized.get("date_created"), errors="coerce", utc=True
    )
    normalized["date_loaded"] = pd.to_datetime(
        normalized.get("date_loaded"), errors="coerce", utc=True
    )
    return normalized


def normalize_incoming_versioned_frame(df: DataFrame) -> DataFrame:
    """Normalize incoming data for historized loading (ensure `is_current`)."""
    normalized = _normalize_versioned_dates(df)
    if "is_current" not in normalized.columns:
        normalized["is_current"] = True
    return normalized


def normalize_existing_versioned_frame(df: DataFrame) -> DataFrame:
    """Normalize existing versioned data (keep only current rows if present)."""
    normalized = _normalize_versioned_dates(df)
    if "is_current" in normalized.columns:
        # Keep only current records. Using `== True` triggers pylint C0121.
        normalized = normalized[normalized["is_current"]].copy()
    return normalized


def prepare_new_versioned_row(row: pd.Series) -> pd.Series:
    """Prepare a new versioned row (set date_created and mark is_current)."""
    prepared = row.copy()
    prepared["date_created"] = (
        prepared["date_created"]
        if pd.notna(prepared["date_created"])
        else prepared["date_loaded"]
    )
    prepared["is_current"] = True
    return prepared


def prepare_changed_versioned_row(
    row: pd.Series, existing_created: object
) -> pd.Series:
    """Prepare a changed row preserving `date_created` when possible."""
    prepared = row.copy()
    prepared["date_created"] = (
        existing_created if pd.notna(existing_created) else prepared["date_loaded"]
    )
    prepared["is_current"] = True
    return prepared


def latest_rows_by_primary_key(df: DataFrame, primary_key: str) -> DataFrame:
    """Return the latest row per `primary_key`, using `date_loaded` if present."""
    latest = df.copy()
    if "date_loaded" in latest.columns:
        latest = latest.sort_values(
            by="date_loaded", ascending=True, na_position="last"
        )
    return (
        latest.dropna(subset=[primary_key])
        .drop_duplicates(subset=[primary_key], keep="last")
    )
