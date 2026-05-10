import os
import logging
from typing import List

logger = logging.getLogger(__name__)


class Embedder:
    def __init__(self, config: dict):
        self.backend = config.get("backend", "local")
        self.model_name = config.get("model_name", "BAAI/bge-small-zh-v1.5")
        self.batch_size = config.get("batch_size", 32)
        self.api_key = config.get("api_key") or os.getenv("DEEPSEEK_API_KEY")
        if self.backend == "local":
            from sentence_transformers import SentenceTransformer
            self.model = SentenceTransformer(self.model_name)
        elif self.backend == "deepseek":
            raise NotImplementedError(
                "DeepSeek embedding backend is not yet implemented. "
                "Please use 'local' backend or implement the API integration."
            )
        else:
            raise ValueError(f"Unsupported backend: {self.backend}")

    def embed(self, texts: List[str]) -> List[List[float]]:
        if not texts:
            return []
        if self.backend == "local":
            # batch encode
            embeddings = self.model.encode(
                texts, batch_size=self.batch_size, show_progress_bar=False
            )
            return embeddings.tolist()
        # Other backends are handled in __init__; this is unreachable for 'deepseek'
        return []
