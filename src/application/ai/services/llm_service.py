from __future__ import annotations

from src.domain.contracts.llm_provider import BaseLLMProvider
from src.domain.models.llm_response import LLMResponse
from src.domain.models.retrieval_result import RetrievalResult


class LLMService:
    def __init__(self, provider: BaseLLMProvider):
        self.provider = provider

    def answer(self, question: str, contexts: list[RetrievalResult]) -> LLMResponse:
        return self.provider.generate(question=question, contexts=contexts)
