from __future__ import annotations

import pandas as pd
from pandas import DataFrame


def _normalize_versioned_dates(df: DataFrame) -> DataFrame:
    normalized = df.copy()
    normalized["date_created"] = pd.to_datetime(
        normalized.get("date_created"), errors="coerce", utc=True
    )
    normalized["date_loaded"] = pd.to_datetime(
        normalized.get("date_loaded"), errors="coerce", utc=True
    )
    return normalized


def normalize_incoming_versioned_frame(df: DataFrame) -> DataFrame:
    normalized = _normalize_versioned_dates(df)
    if "is_current" not in normalized.columns:
        normalized["is_current"] = True
    return normalized


def normalize_existing_versioned_frame(df: DataFrame) -> DataFrame:
    normalized = _normalize_versioned_dates(df)
    if "is_current" in normalized.columns:
        normalized = normalized[normalized["is_current"] == True].copy()
    return normalized


def prepare_new_versioned_row(row: pd.Series) -> pd.Series:
    prepared = row.copy()
    prepared["date_created"] = (
        prepared["date_created"]
        if pd.notna(prepared["date_created"])
        else prepared["date_loaded"]
    )
    prepared["is_current"] = True
    return prepared


def prepare_changed_versioned_row(row: pd.Series, existing_created) -> pd.Series:
    prepared = row.copy()
    prepared["date_created"] = (
        existing_created if pd.notna(existing_created) else prepared["date_loaded"]
    )
    prepared["is_current"] = True
    return prepared


def latest_rows_by_primary_key(df: DataFrame, primary_key: str) -> DataFrame:
    latest = df.copy()
    if "date_loaded" in latest.columns:
        latest = latest.sort_values(by="date_loaded", ascending=True, na_position="last")
    return latest.dropna(subset=[primary_key]).drop_duplicates(subset=[primary_key], keep="last")
