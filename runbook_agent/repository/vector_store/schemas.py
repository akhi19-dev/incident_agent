from pydantic import BaseModel
from typing import List, Optional
from lancedb.pydantic import Vector


# Define the schema using Pydantic
class VectorTable(BaseModel):
    """
    Define the table schema
    """

    doc_id: str
    vector: Vector(512)
    text: str
    file_name: str
    page_label: Optional[str] = None

    @classmethod
    def get_vector_field(cls) -> str:
        """
        Return the name of the field that holds the vector data (hardcoded here as 'vector').
        This can be extended to dynamically handle multiple vector fields.
        """
        return "vector"

    @classmethod
    def get_doc_id_field(cls) -> str:
        return "doc_id"

    @classmethod
    def get_text_field(cls) -> str:
        return "text"

    @classmethod
    def get_file_name_field(cls) -> str:
        return "file_name"

    @classmethod
    def get_page_label_field(cls) -> str:
        return "page_label"


class QueryDocId(BaseModel):
    doc_id: str


class QueryVectors(BaseModel):
    query_vector: List[float]
    k: int = 5


class SearchResult(BaseModel):
    doc_id: str
    distance: float
    text: str
    file_name: str
    page_label: Optional[str]
