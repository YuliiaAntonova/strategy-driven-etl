from datetime import datetime, timezone
import hashlib

from pandas import DataFrame

from src.domain.contracts.transformer import BaseTransformer
from src.domain.models.pipeline_context import PipelineContext


class JobsAuditTransformer(BaseTransformer):
    def __init__(self, context: PipelineContext, source_name: str):
        self.context = context
        self.source_name = source_name

    @staticmethod
    def _build_stable_id(row) -> str:
        job_url = str(row.get("job_url", "") or "").strip().lower()
        site = str(row.get("site", "") or "").strip().lower()

        # если job_url есть, используем его как основу для стабильного id
        if job_url:
            raw_key = f"{site}::{job_url}"
        else:
            # fallback, если job_url пустой
            company = str(row.get("company", "") or "").strip().lower()
            title = str(row.get("title", "") or "").strip().lower()
            location = str(row.get("location", "") or "").strip().lower()
            raw_key = f"{site}::{company}::{title}::{location}"

        return hashlib.md5(raw_key.encode("utf-8")).hexdigest()

    def transform(self, df: DataFrame) -> DataFrame:
        result = df.copy()
        now = datetime.now(timezone.utc)

        if "id" not in result.columns:
            result["id"] = result.apply(self._build_stable_id, axis=1)

        result["source_name"] = self.source_name
        result["run_id"] = self.context.run_id
        result["dt"] = self.context.dt
        result["date_created"] = now
        result["date_loaded"] = now
        result["environment"] = self.context.environment
        result["is_current"] = True

        return result