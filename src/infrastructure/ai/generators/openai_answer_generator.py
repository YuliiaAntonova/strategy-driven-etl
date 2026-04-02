from __future__ import annotations

from src.domain.contracts.answer_generator import BaseAnswerGenerator
from src.domain.models.llm_response import LLMResponse
from src.domain.models.retrieval_result import RetrievalResult


class OpenAIAnswerGenerator(BaseAnswerGenerator):
    def __init__(self, model: str, api_key: str):
        self.model = model
        self.api_key = api_key

    def generate(self, prompt: str, contexts: list[RetrievalResult]) -> LLMResponse:
        if not self.api_key:
            raise ValueError("OPENAI_API_KEY is required for the openai answer generator")

        try:
            from openai import OpenAI
        except ImportError as exc:
            raise ImportError("Install the 'openai' package to use the openai answer generator") from exc

        client = OpenAI(api_key=self.api_key)
        response = client.responses.create(
            model=self.model,
            input=prompt,
        )
        text = getattr(response, "output_text", "").strip()
        if not text:
            text = "No answer returned by the model."
        return LLMResponse(
            text=text,
            metadata={
                "matches": str(len(contexts)),
                "generator": "openai",
                "model": self.model,
            },
        )
