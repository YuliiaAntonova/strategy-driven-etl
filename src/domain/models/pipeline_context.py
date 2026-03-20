from dataclasses import dataclass
from datetime import datetime, timezone


@dataclass(slots=True)
class PipelineContext:
    dataset: str
    dt: str
    run_id: str
    environment: str = "local"

    @staticmethod
    def utc_today() -> str:
        return datetime.now(timezone.utc).strftime("%Y-%m-%d")

    @staticmethod
    def utc_run_id() -> str:
        return datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
