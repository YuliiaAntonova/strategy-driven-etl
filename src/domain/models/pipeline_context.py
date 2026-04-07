"""Run-scoped context values shared across pipeline components."""

from dataclasses import dataclass
from datetime import datetime, timezone


@dataclass(slots=True)
class PipelineContext:
    """Minimal context for one pipeline run (dataset, time, run id, env)."""

    dataset: str
    dt: str
    run_id: str
    environment: str = "local"

    @staticmethod
    def utc_today() -> str:
        """Return today's date in UTC as `YYYY-MM-DD`."""
        return datetime.now(timezone.utc).strftime("%Y-%m-%d")

    @staticmethod
    def utc_run_id() -> str:
        """Return a UTC run identifier as `YYYYMMDDTHHMMSSZ`."""
        return datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
