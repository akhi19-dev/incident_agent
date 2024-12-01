import logging
from runbook_agent.embedding_provider.base_embedding_provider import (
    BaseEmbeddingProvider,
)
from runbook_agent.repository.vector_store.vector_store_service import (
    VectorStoreService,
)
from runbook_agent.repository.vector_store.schemas import QueryVectors

# Initialize configuration and logger
logging = logging.getLogger(__name__)


class QueryEngine:
    def __init__(
        self,
        embedding_provider: BaseEmbeddingProvider,  # The embedding provider instance
        vector_store: VectorStoreService,  # The vector store instance (Faiss, Qdrant, etc.)
        top_k: int = 5,  # The number of top results to fetch
    ):
        """
        Initialize the query engine with the provided embedding provider and vector store.

        Args:
            embedding_provider (BaseEmbeddingRepository): The embedding provider instance.
            vector_store (VectorStoreService): The vector store instance (Faiss, Qdrant, etc.).
            top_k (int): The number of top k results to return from the query.
        """
        self.embedding_provider = embedding_provider
        self.vector_store = vector_store
        self.top_k = top_k

    def _get_embedding(self, query_text: str):
        """
        Get embeddings for the query text using the embedding provider.

        Args:
            query_text (str): The query text to be embedded.

        Returns:
            list: The embedding vector of the query.
        """
        return self.embedding_provider.get_text_embedding(query_text)

    def query_vector_store(self, query_text: str):
        """
        Query the vector store with the provided query text.

        Args:
            query_text (str): The query text to search for.

        Returns:
            list: A list of top k results from the vector store.
        """
        # Get embedding for the query
        query_embedding = self._get_embedding(query_text)

        # Construct query vectors for vector store
        query_vectors = QueryVectors(query_vector=query_embedding, k=self.top_k)

        # Query the vector store for top k results
        results = self.vector_store.query_vectors(query_vectors)

        return results

