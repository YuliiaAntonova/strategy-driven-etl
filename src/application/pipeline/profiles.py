from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class PipelineProfile:
    name: str
    detector_key: str
    initial_writer_key: str
    subsequent_writer_key: str
    requires_primary_key: bool = False


PIPELINE_PROFILES: dict[str, PipelineProfile] = {
    "full_refresh": PipelineProfile(
        name="full_refresh",
        detector_key="full",
        initial_writer_key="replace",
        subsequent_writer_key="append",
        requires_primary_key=False,
    ),
    "historized_snapshot": PipelineProfile(
        name="historized_snapshot",
        detector_key="incremental-by-primary-key-and-hash",
        initial_writer_key="versioned",
        subsequent_writer_key="versioned",
        requires_primary_key=True,
    ),
}

DEFAULT_WRITE_MODE_BY_LOAD_MODE = {
    "full": "replace",
    "incremental-by-date": "versioned",
    "incremental-by-primary-key": "versioned",
    "incremental-by-hash": "versioned",
    "incremental-by-primary-key-and-hash": "versioned",
}

ALLOWED_WRITERS_BY_LOAD_MODE = {
    "full": {"replace"},
    "incremental-by-date": {"versioned"},
    "incremental-by-primary-key": {"versioned"},
    "incremental-by-hash": {"versioned"},
    "incremental-by-primary-key-and-hash": {"versioned"},
}
