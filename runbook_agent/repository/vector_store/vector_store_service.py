# app/vector_store/vector_store_service.py

from typing import List
from runbook_agent.repository.vector_store.base_repository import VectorBaseRepository
from runbook_agent.repository.vector_store.lance_db import LanceDBRepository
from runbook_agent.repository.vector_store.schemas import (
    VectorTable,
    QueryDocId,
    QueryVectors,
)
from runbook_agent.repository.vector_store.models import VectorStores


class VectorStoreService:
    """
    A service that abstracts interaction with the vector store repositories.
    It dynamically selects the correct repository (LanceDB, Qdrant, FAISS) based on configuration.
    """

    def __init__(self, vector_store_name: VectorStores, table_name: str):
        """
        Initialize the service with the vector store type and optional parameters like schema and client.

        Args:
            vector_store_name (str): The name of the vector store (e.g., "lancedb", "qdrant", "faiss").
            table_name (str): The table/collection name in the vector store.
            schema (optional): Schema for LanceDB (if applicable).
            client (optional): Client for external vector stores (like Qdrant).
        """
        self.vector_store_name = vector_store_name
        self.table_name = table_name
        self.repository = self._initialize_repository()

    def _initialize_repository(self) -> VectorBaseRepository:
        """
        Initialize the appropriate repository (LanceDB, Qdrant, FAISS) based on the vector store name.

        Returns:
            BaseRepository: An instance of the correct repository.
        """
        if self.vector_store_name == VectorStores.LANCEDB:
            # Initialize LanceDB repository
            return LanceDBRepository(table_name=self.table_name)

        else:
            raise ValueError(f"Unsupported vector store: {self.vector_store_name}")

    def insert_vectors(self, vectors: List[VectorTable]):
        """
        Insert vectors into the selected vector store via the repository.

        Args:
            vectors (List[VectorTable]): List of vectors to insert.
        """
        self.repository.insert_vectors(vectors)

    def query_vectors(self, query: QueryVectors):
        """
        Query vectors from the selected vector store via the repository.

        Args:
            query (List[QueryVectors]): Query to search for vectors.
        """
        return self.repository.query_vectors(query)

    def delete_by_doc_ids(self, query: List[QueryDocId]):
        """
        Delete vectors based on document name from the vector store.

        Args:
            query (QueryDocName): Query with document name for deletion.
        """
        self.repository.delete_by_doc_ids(query)

    def create_index(self):
        """
        Create index on table
        """
        self.repository.create_index()
