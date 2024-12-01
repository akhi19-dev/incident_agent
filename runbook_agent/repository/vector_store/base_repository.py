# app/vector_store/base_repository.py
from abc import ABC, abstractmethod
from runbook_agent.repository.vector_store.schemas import (
    VectorTable,
    QueryDocId,
    QueryVectors,
)
from typing import List


class VectorBaseRepository(ABC):
    """
    Abstract Base class for vector store repositories.
    This class outlines the methods that any repository must implement.
    """

    @abstractmethod
    def insert_vectors(self, vectors: List[VectorTable]):
        """
        Inserts vectors into the specified table.
        """
        pass

    @abstractmethod
    def query_vectors(self, query: QueryVectors):
        """
        Queries vectors from the specified table.
        """
        pass

    @abstractmethod
    def delete_by_doc_ids(self, query: List[QueryDocId]):
        """
        Queries vectors from the specified table.
        """
        pass

    @abstractmethod
    def create_index(self):
        """
        Queries vectors from the specified table.
        """
        pass
