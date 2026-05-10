import os
from typing import List
from tenacity import retry, stop_after_attempt, wait_exponential
import numpy as np

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
            # Not implemented yet, placeholder
            pass
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
        elif self.backend == "deepseek":
            return self._embed_via_api(texts)
        return []

    @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=1, max=10))
    def _embed_via_api(self, texts: List[str]) -> List[List[float]]:
        # Placeholder for DeepSeek embedding API (if they provide one)
        # You could adapt to OpenAI API style if using other provider
        import requests
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }
        payload = {
            "model": "deepseek-embed",  # hypothetical
            "input": texts,
        }
        # Note: DeepSeek does not officially provide an embedding API yet.
        # This endpoint is a placeholder for future compatibility or custom proxy.
        # For production, consider using OpenAI-compatible APIs (e.g., text-embedding-3-small).
        resp = requests.post(
            "https://api.deepseek.com/v1/embeddings",
            json=payload,
            headers=headers,
            timeout=60,
        )
        resp.raise_for_status()
        data = resp.json()
        return [item["embedding"] for item in data["data"]]
