# app/vector_store/lancedb_repository.py
from runbook_agent.repository.vector_store.base_repository import VectorBaseRepository
from runbook_agent.repository.vector_store.schemas import (
    VectorTable,
    QueryDocId,
    QueryVectors,
    SearchResult,
)
from runbook_agent.clients.lance_db import lancedb_client
from typing import List
from lancedb.pydantic import pydantic_to_schema


# TODO : Check how concurrent writes are handled and implement necessary changes
class LanceDBRepository(VectorBaseRepository):
    """
    LanceDB repository implementation for vector storage.
    """

    def __init__(self, table_name: str):
        """
        Initialize the LanceDB repository with the provided LanceDB client.

        Args:
        client (LanceDBClient): The LanceDB client instance.
        """
        self.client = lancedb_client
        self.table = None
        self._create_table(table_name=table_name)
        self.refine_factor = 3

    def _create_table(self, table_name: str):
        """
        Create a table in LanceDB with the provided schema if it doesn't exist.

        Args:
            table_name (str): Name of the table to be created.
            schema_name (BaseModel): The schema name to be used for the table.
        """
        schema_dict = pydantic_to_schema(VectorTable)
        existing_tables = self.client.table_names()
        if table_name not in existing_tables:
            self.table = self.client.create_table(name=table_name, schema=schema_dict)
        else:
            self.table = self.client.open_table(name=table_name)

    def create_index(self):
        sub_vectors = 8
        partitions = int((self.table.count_rows() * sub_vectors) / 20000)
        if partitions <= 0:
            return
        self.table.create_index(
            index_type="IVF_HNSW_PQ",
            metric="cosine",
            num_partitions=partitions,
            num_sub_vectors=sub_vectors,
            index_cache_size=102800,
        )

    def insert_vectors(self, vectors: List[VectorTable]):
        """
        Inserts vectors into the specified table in LanceDB.

        Args:
            table_name (str): The table where vectors will be inserted.
            vectors (list): List of vectors (dictionaries) to be inserted.
        """
        vectors_dict = [vector.model_dump() for vector in vectors]
        self.table.add(vectors_dict)

    def delete_by_doc_ids(self, query_data: List[QueryDocId]):
        """
        Deletes documents from the table based on 'doc_id'.

        Args:
            table_name (str): The table from which documents will be deleted.
            doc_id (str): The document name to filter on.

        Raises:
            Exception: If deletion fails.
        """
        doc_ids = [query.doc_id for query in query_data]
        doc_ids_string = ", ".join([f"'{str(v)}'" for v in doc_ids])
        self.table.delete(f"{VectorTable.get_doc_id_field()} IN ({doc_ids_string})")

    def query_vectors(self, query_data: QueryVectors):
        """
        Queries vectors from the table using the given query.

        Args:
            query_data (List[QueryVectors]): List of query data, each item being a query object.
        """
        # Convert query objects to dictionary format
        results = (
            self.table.search(query=query_data.query_vector, query_type="vector")
            .limit(query_data.k)
            .refine_factor(self.refine_factor)
            .metric("cosine")
        )
        resultsList = results.to_list()
        search_results = [
            SearchResult(
                doc_id=resultsList[i][VectorTable.get_doc_id_field()],
                distance=resultsList[i]["_distance"],
                text=resultsList[i][VectorTable.get_text_field()],
                file_name=resultsList[i][VectorTable.get_file_name_field()],
                page_label=resultsList[i][VectorTable.get_page_label_field()],
            )
            for i in range(len(resultsList))
        ]
        return search_results
