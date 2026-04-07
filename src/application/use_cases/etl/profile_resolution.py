"""Profile resolution for the ETL use case.

Either a named pipeline profile is selected, or a profile is derived from
(load_mode, write_mode) with validation.
"""

from __future__ import annotations

from src.application.pipeline.profiles import (
    ALLOWED_WRITERS_BY_LOAD_MODE,
    DEFAULT_WRITE_MODE_BY_LOAD_MODE,
    PIPELINE_PROFILES,
    PipelineProfile,
)
from src.application.use_cases.etl.config import RunEtlConfig


def resolve_runtime_profile(config: RunEtlConfig) -> PipelineProfile:
    """Resolve the runtime profile based on config."""

    if config.profile:
        try:
            return PIPELINE_PROFILES[config.profile]
        except KeyError:
            raise ValueError(f"Unsupported profile: {config.profile}") from None

    resolved_write_mode = config.write_mode or DEFAULT_WRITE_MODE_BY_LOAD_MODE[config.load_mode]
    allowed_writers = ALLOWED_WRITERS_BY_LOAD_MODE[config.load_mode]
    if resolved_write_mode not in allowed_writers:
        allowed = ", ".join(sorted(allowed_writers))
        raise ValueError(f"{config.load_mode} supports only write-mode(s): {allowed}")

    writer_for_later_batches = "append" if config.load_mode == "full" else resolved_write_mode
    requires_primary_key = config.load_mode != "full"
    return PipelineProfile(
        name=f"{config.load_mode}:{resolved_write_mode}",
        detector_key=config.load_mode,
        initial_writer_key=resolved_write_mode,
        subsequent_writer_key=writer_for_later_batches,
        requires_primary_key=requires_primary_key,
    )

