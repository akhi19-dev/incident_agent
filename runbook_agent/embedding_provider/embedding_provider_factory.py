from runbook_agent.embedding_provider.base_embedding_provider import (
    BaseEmbeddingProvider,
)
from runbook_agent.embedding_provider.bedrock_embedding_provider import (
    BedrockEmbeddingProvider,
)
from runbook_agent.embedding_provider.models import (
    EmbeddingModels,
)
from llama_index.embeddings.openai import OpenAIEmbedding
import os


class EmbeddingServiceFactory:
    """
    Factory to create instances of embedding service repositories based on the provider type.
    """

    @staticmethod
    def create_embedding_service(
        provider_type: EmbeddingModels, model_id: str, *args, **kwargs
    ) -> BaseEmbeddingProvider:
        """
        Creates the embedding service based on the provider type.

        Args:
            provider_type (str): Type of the embedding provider (e.g., "bedrock", "openai").
            model_id (str): The model ID to initialize the embedding provider (e.g., Bedrock's model ID).
            *args, **kwargs: Additional arguments passed to the embedding provider initialization.

        Returns:
            BaseEmbeddingRepository: A repository wrapping the embedding provider.
        """
        if provider_type == EmbeddingModels.BEDROCK:
            embedding_provider = BedrockEmbeddingProvider(
                model_id=model_id, *args, **kwargs
            )
        if provider_type == EmbeddingModels.OPENAI:
            embedding_provider = OpenAIEmbedding(
                model=model_id,
                dimensions=512,
                api_key=os.getenv("OPENAI_API_KEY"),
            )
        else:
            raise ValueError(f"Unsupported provider type: {provider_type}")

        # Wrap the embedding provider with the repository
        return embedding_provider
