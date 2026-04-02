from __future__ import annotations

from collections.abc import Callable

from src.domain.contracts.chunker import BaseChunker
from src.domain.contracts.embedder import BaseEmbedder
from src.domain.contracts.answer_generator import BaseAnswerGenerator
from src.domain.contracts.llm_provider import BaseLLMProvider
from src.domain.contracts.prompt_builder import BasePromptBuilder
from src.domain.contracts.reranker import BaseReranker
from src.domain.contracts.retriever import BaseRetriever
from src.infrastructure.ai.chunkers.recursive_text_chunker import RecursiveTextChunker
from src.infrastructure.ai.embedders.token_frequency_embedder import TokenFrequencyEmbedder
from src.infrastructure.ai.generators.openai_answer_generator import OpenAIAnswerGenerator
from src.infrastructure.ai.generators.template_answer_generator import TemplateAnswerGenerator
from src.infrastructure.ai.prompts.grounded_answer_prompt_builder import GroundedAnswerPromptBuilder
from src.infrastructure.ai.providers.template_llm_provider import TemplateLLMProvider
from src.infrastructure.ai.rerankers.keyword_metadata_reranker import KeywordMetadataReranker
from src.infrastructure.ai.retrievers.keyword_retriever import KeywordRetriever
from src.config.settings import settings


ChunkerFactory = Callable[[int, int], BaseChunker]
EmbedderFactory = Callable[[], BaseEmbedder]
RetrieverFactory = Callable[[], BaseRetriever]
LLMProviderFactory = Callable[[], BaseLLMProvider]
RerankerFactory = Callable[[], BaseReranker]
PromptBuilderFactory = Callable[[], BasePromptBuilder]
AnswerGeneratorFactory = Callable[[], BaseAnswerGenerator]


CHUNKER_FACTORIES: dict[str, ChunkerFactory] = {
    "recursive": lambda chunk_size, chunk_overlap: RecursiveTextChunker(
        chunk_size=chunk_size,
        chunk_overlap=chunk_overlap,
    ),
}

EMBEDDER_FACTORIES: dict[str, EmbedderFactory] = {
    "token_frequency": TokenFrequencyEmbedder,
}

RETRIEVER_FACTORIES: dict[str, RetrieverFactory] = {
    "keyword": KeywordRetriever,
}

LLM_PROVIDER_FACTORIES: dict[str, LLMProviderFactory] = {
    "template": TemplateLLMProvider,
}


RERANKER_FACTORIES: dict[str, RerankerFactory] = {
    "keyword_metadata": KeywordMetadataReranker,
}

PROMPT_BUILDER_FACTORIES: dict[str, PromptBuilderFactory] = {
    "grounded": GroundedAnswerPromptBuilder,
}

ANSWER_GENERATOR_FACTORIES: dict[str, AnswerGeneratorFactory] = {
    "template": TemplateAnswerGenerator,
    "openai": lambda: OpenAIAnswerGenerator(model=settings.openai_model, api_key=settings.openai_api_key),
}
