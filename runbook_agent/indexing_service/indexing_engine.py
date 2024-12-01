import logging
from runbook_agent.embedding_provider.base_embedding_provider import (
    BaseEmbeddingProvider,
)
from runbook_agent.repository.vector_store.vector_store_service import (
    VectorStoreService,
)
from runbook_agent.repository.vector_store.schemas import VectorTable

# Initialize configuration and logger
logging = logging.getLogger(__name__)


class IndexingEngine:
    def __init__(
        self,
        embedding_provider: BaseEmbeddingProvider,  # The embedding provider instance
        vector_store: VectorStoreService,  # The vector store instance
    ):
        """
        Initialize the indexing engine with the provided embedding provider and vector store.

        Args:
            embedding_provider (BaseEmbeddingRepository): The embedding provider instance.
            vector_store (VectorStoreService): The vector store instance (Faiss, Qdrant, etc.).
        """
        self.embedding_provider = embedding_provider
        self.vector_store = vector_store

    def insert_text_to_vector_store(
        self, doc_id: str, file_name: str, label: str, text: str
    ):
        """
        Insert a single description (text) into the vector store.

        Args:
            text (str): The description text to be inserted.

        Returns:
            bool: True if the text is successfully inserted, False otherwise.
        """
        try:
            # Get embeddings for the text
            embeddings = self.embedding_provider.get_text_embedding(text)

            # Create a vector document to be inserted (here we use a hash of the text as doc_id)
            vector_doc = VectorTable(
                doc_id=doc_id,
                vector=embeddings,
                text=text,
                file_name=file_name,
                page_label=label,
            )

            # Insert the vector into the vector store
            self.vector_store.insert_vectors([vector_doc])
        except Exception as e:
            raise e
