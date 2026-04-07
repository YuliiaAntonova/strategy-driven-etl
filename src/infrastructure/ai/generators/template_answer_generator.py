"""A simple deterministic answer generator.

This generator produces a human-readable summary using only the retrieved
contexts. It is useful as a fallback when no LLM provider is configured.
"""

from __future__ import annotations

from src.domain.contracts.answer_generator import BaseAnswerGenerator
from src.domain.models.llm_response import LLMResponse
from src.domain.models.retrieval_result import RetrievalResult


class TemplateAnswerGenerator(BaseAnswerGenerator):
    """Generate a basic grounded answer without calling an external LLM."""

    def generate(self, prompt: str, contexts: list[RetrievalResult]) -> LLMResponse:
        if not contexts:
            return LLMResponse(
                text=(
                    "I could not find enough indexed context to answer this question. "
                    "Try a more specific question or run AI indexing again."
                ),
                metadata={"matches": "0", "generator": "template"},
            )

        lines = ["Grounded answer based on indexed jobs:", ""]
        for idx, item in enumerate(contexts, start=1):
            title = item.metadata.get("title", item.entity_id)
            company = item.metadata.get("company", "")
            location = item.metadata.get("location", "")
            skills = item.metadata.get("skills", "")
            job_url = item.metadata.get("job_url", "")
            descriptor = " | ".join(part for part in [title, company, location] if part)
            lines.append(
                f"[{idx}] {descriptor}" if descriptor else f"[{idx}] {item.entity_id}"
            )
            if skills:
                lines.append(f"skills: {skills}")
            lines.append(item.content[:320].replace("\n", " ").strip())
            if job_url:
                lines.append(f"url: {job_url}")
            lines.append("")
        return LLMResponse(
            text="\n".join(lines).strip(),
            metadata={"matches": str(len(contexts)), "generator": "template"},
        )
