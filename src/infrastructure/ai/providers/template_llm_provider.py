"""Template (non-LLM) provider.

This provider returns a deterministic response built from retrieved contexts.
It is useful as a safe default when no external LLM is configured.
"""

from __future__ import annotations

from src.domain.contracts.llm_provider import BaseLLMProvider
from src.domain.models.llm_response import LLMResponse
from src.domain.models.retrieval_result import RetrievalResult


class TemplateLLMProvider(BaseLLMProvider):
    """Generate a response without calling an external LLM."""

    def generate(self, question: str, contexts: list[RetrievalResult]) -> LLMResponse:
        if not contexts:
            return LLMResponse(
                text=(
                    "I could not find relevant current chunks for this question. "
                    "Try a more specific query or refresh AI indexing."
                ),
                metadata={"matches": "0"},
            )

        lines = [f"Question: {question}", "", "Top relevant results:"]
        for idx, item in enumerate(contexts, start=1):
            title = item.metadata.get("title", item.entity_id)
            company = item.metadata.get("company", "")
            location = item.metadata.get("location", "")
            job_url = item.metadata.get("job_url", "")
            snippet = item.content[:280].replace("\n", " ").strip()
            descriptor = " | ".join(part for part in [title, company, location] if part)
            lines.append(
                f"{idx}. {descriptor}" if descriptor else f"{idx}. {item.entity_id}"
            )
            lines.append(f"   score={item.score}")
            if snippet:
                lines.append(f"   {snippet}")
            if job_url:
                lines.append(f"   url: {job_url}")
        return LLMResponse(
            text="\n".join(lines),
            metadata={"matches": str(len(contexts))},
        )
