from abc import ABC, abstractmethod
from typing import List, Any
from runbook_agent.embedding_provider.models import Embedding


class BaseEmbeddingProvider(ABC):
    """
    Abstract Base class for embedding providers.
    This class outlines the methods that any embedding provider should implement.
    """

    @abstractmethod
    def get_text_embedding(self, text: str) -> Embedding:
        """
        Get embeddings for the provided text.

        Args:
            text (str): The input text to get embeddings for.

        Returns:
            List[float]: A list of embedding values.
        """
        pass

    def get_text_embedding_batch(
        self,
        texts: List[str],
        show_progress: bool = False,
        **kwargs: Any,
    ) -> List[Embedding]:
        """Get a list of text embeddings, with batching."""
        pass
