"""OpenAI-based answer generator.

The OpenAI dependency is optional: the import is deferred and a helpful error
message is raised if the package is not installed.
"""

from __future__ import annotations

import importlib

from functools import lru_cache
from typing import TYPE_CHECKING

from src.domain.contracts.answer_generator import BaseAnswerGenerator
from src.domain.models.llm_response import LLMResponse
from src.domain.models.retrieval_result import RetrievalResult

if TYPE_CHECKING:  # pragma: no cover
    from openai import OpenAI  # noqa: F401


@lru_cache(maxsize=1)
def _openai_client_class():
    """Return the OpenAI client class, importing it only when needed."""
    try:
        module = importlib.import_module("openai")
        openai_client_cls = getattr(module, "OpenAI")
    except ImportError as exc:  # pragma: no cover
        raise ImportError(
            "Install the 'openai' package to use the OpenAI answer generator"
        ) from exc
    return openai_client_cls


class OpenAIAnswerGenerator(BaseAnswerGenerator):
    """Generate answers using OpenAI's Responses API."""

    def __init__(self, model: str, api_key: str):
        self.model = model
        self.api_key = api_key

    def generate(self, prompt: str, contexts: list[RetrievalResult]) -> LLMResponse:
        if not self.api_key:
            raise ValueError(
                "OPENAI_API_KEY is required for the OpenAI answer generator"
            )

        client_cls = _openai_client_class()
        client = client_cls(api_key=self.api_key)
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
