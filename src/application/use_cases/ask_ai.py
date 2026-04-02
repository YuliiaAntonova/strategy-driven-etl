from __future__ import annotations

from src.application.ai.builders.grounded_answer_builder import GroundedAnswerServiceBuilder
from src.config.settings import settings


def ask_ai(question: str, profile: str | None = None, top_k: int | None = None, fetch_k: int | None = None, connector=None) -> str:
    service = GroundedAnswerServiceBuilder.build(profile=profile, connector=connector)
    result = service.answer(
        question=question,
        fetch_k=fetch_k or settings.ai_fetch_k,
        top_k=top_k or settings.ai_top_k,
    )
    return result.text
