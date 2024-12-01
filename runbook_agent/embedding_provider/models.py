from typing import List
from enum import Enum

Embedding = List[float]


class BedrockModels(Enum):
    TITAN_TEXT_EMBEDDING_V2 = "amazon.titan-embed-text-v2:0"


class OPENAIModels(Enum):
    TEXT_EMBEDDING_3_SMALL = "text-embedding-3-small"


class EmbeddingModels(Enum):
    BEDROCK = "bedrock"
    OPENAI = "openai"
