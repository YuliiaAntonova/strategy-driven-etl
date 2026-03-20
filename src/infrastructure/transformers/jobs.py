from datetime import datetime, timezone

from pandas import DataFrame

from src.domain.contracts.transformer import BaseTransformer
from src.domain.models.pipeline_context import PipelineContext


class JobsAuditTransformer(BaseTransformer):
    def __init__(self, context: PipelineContext, source_name: str):
        self.context = context
        self.source_name = source_name

    def transform(self, df: DataFrame) -> DataFrame:
        result = df.copy()
        now = datetime.now(timezone.utc)

        result["source_name"] = self.source_name
        result["run_id"] = self.context.run_id
        result["dt"] = self.context.dt
        result["date_created"] = now
        result["date_loaded"] = now
        result["environment"] = self.context.environment
        result["is_current"] = True

        return result