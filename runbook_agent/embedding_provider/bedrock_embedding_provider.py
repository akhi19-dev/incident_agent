import json
from runbook_agent.clients.bedrock_runtime_client import bedrock_runtime_client
from typing import List, Any
from llama_index.core.utils import get_tqdm_iterable
from runbook_agent.embedding_provider.models import Embedding
from runbook_agent.config import init_config

cfg = init_config()


class BedrockEmbeddingProvider:
    def __init__(self, model_id: str):
        """
        Initialize the Bedrock client and embedding provider for generating embeddings.

        Args:
            model_id (str): The ID of the Bedrock embedding model.
            region_name (str): The AWS region where the Bedrock service is available.
        """
        self.client = bedrock_runtime_client
        self.model_id = model_id
        self.embed_batch_size = 10

    def get_text_embedding(self, text: str) -> Embedding:
        """
        Get embeddings from Bedrock for the provided text.

        Args:
            text (str): The input text to get embeddings for.

        Returns:
            List[float]: The list of embedding values.
        """
        response = self.client.invoke_model(
            modelId=self.model_id,
            body=json.dumps(
                {
                    "inputText": text,
                    "dimensions": 512,
                    "normalize": True,
                }
            ),
            contentType="application/json",
            accept="application/json",
        )

        response_body = json.loads(response.get("body").read())
        embeddings = response_body["embedding"]
        return embeddings

    def _get_text_embeddings(self, texts: List[str]) -> List[Embedding]:
        """
        Embed the input sequence of text synchronously.

        Subclasses can implement this method if batch queries are supported.
        """
        # Default implementation just loops over _get_text_embedding
        return [self.get_text_embedding(text) for text in texts]

    def get_text_embedding_batch(
        self,
        texts: List[str],
        show_progress: bool = False,
        **kwargs: Any,
    ) -> List[Embedding]:
        """Get a list of text embeddings, with batching."""
        cur_batch: List[str] = []
        result_embeddings: List[Embedding] = []

        queue_with_progress = enumerate(
            get_tqdm_iterable(texts, show_progress, "Generating embeddings")
        )

        for idx, text in queue_with_progress:
            cur_batch.append(text)
            if idx == len(texts) - 1 or len(cur_batch) == self.embed_batch_size:
                embeddings = self._get_text_embeddings(cur_batch)
                result_embeddings.extend(embeddings)
                cur_batch = []

        return result_embeddings
