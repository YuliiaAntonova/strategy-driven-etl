from __future__ import annotations

from collections.abc import Callable

from src.domain.contracts.chunker import BaseChunker
from src.domain.contracts.embedder import BaseEmbedder
from src.domain.contracts.llm_provider import BaseLLMProvider
from src.domain.contracts.retriever import BaseRetriever
from src.infrastructure.ai.chunkers.recursive_text_chunker import RecursiveTextChunker
from src.infrastructure.ai.embedders.token_frequency_embedder import TokenFrequencyEmbedder
from src.infrastructure.ai.providers.template_llm_provider import TemplateLLMProvider
from src.infrastructure.ai.retrievers.keyword_retriever import KeywordRetriever


ChunkerFactory = Callable[[int, int], BaseChunker]
EmbedderFactory = Callable[[], BaseEmbedder]
RetrieverFactory = Callable[[], BaseRetriever]
LLMProviderFactory = Callable[[], BaseLLMProvider]


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
