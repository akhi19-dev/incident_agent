from runbook_agent.embedding_provider.base_embedding_provider import (
    BaseEmbeddingProvider,
)
from typing import List, Any
from runbook_agent.embedding_provider.models import Embedding


class BaseEmbeddingRepository(BaseEmbeddingProvider):
    def __init__(self, embedding_provider: BaseEmbeddingProvider):
        """
        A wrapper for embedding providers to add additional logic (e.g., logging, caching, etc.)

        Args:
            embedding_provider (BaseEmbeddingProvider): The actual embedding provider instance (e.g. Bedrock, OpenAI).
        """
        self.__embedding_provider = embedding_provider

    def get_text_embedding(self, text: str) -> Embedding:
        """
        Calls the actual embedding provider's `get_embeddings` method.

        Args:
            text (str): The input text to get embeddings for.

        Returns:
            List[float]: The list of embedding values.
        """
        embeddings = self.__embedding_provider.get_text_embedding(text)
        return embeddings

    def get_text_embedding_batch(
        self,
        texts: List[str],
        show_progress: bool = False,
        **kwargs: Any,
    ) -> List[Embedding]:
        return self.__embedding_provider.get_text_embedding_batch(
            texts=texts, show_progress=show_progress, kwargs=kwargs
        )
