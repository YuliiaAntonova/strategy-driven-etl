from __future__ import annotations

from src.domain.contracts.prompt_builder import BasePromptBuilder
from src.domain.models.retrieval_result import RetrievalResult


class GroundedAnswerPromptBuilder(BasePromptBuilder):
    def build(self, question: str, contexts: list[RetrievalResult]) -> str:
        if not contexts:
            return (
                "You are a grounded assistant. No retrieval context was found. "
                "Answer that there is not enough indexed data and suggest refreshing AI indexing or asking a more specific question.\n\n"
                f"Question: {question}"
            )

        context_blocks: list[str] = []
        for idx, item in enumerate(contexts, start=1):
            descriptor = " | ".join(
                part for part in [
                    item.metadata.get("title", ""),
                    item.metadata.get("company", ""),
                    item.metadata.get("location", ""),
                ] if part
            )
            job_url = item.metadata.get("job_url", "")
            lines = [f"[{idx}] {descriptor or item.entity_id}", f"score={item.score}", item.content.strip()]
            if job_url:
                lines.append(f"job_url={job_url}")
            context_blocks.append("\n".join(lines))

        context_text = "\n\n".join(context_blocks)
        return (
            "You are a grounded jobs assistant. Use only the retrieved context below. "
            "Do not invent companies, salaries, skills, locations, or links. "
            "If the answer is incomplete, say exactly what is missing. "
            "Prefer a short direct answer first, then a compact bullet list of matching jobs when available. "
            "When possible, cite source numbers like [1], [2].\n\n"
            f"Question:\n{question}\n\n"
            f"Retrieved context:\n{context_text}"
        )
