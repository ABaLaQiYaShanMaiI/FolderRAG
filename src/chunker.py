import hashlib
from typing import List, Dict, Any


class Chunker:
    def __init__(self, config: dict):
        self.max_tokens = config.get("max_tokens", 500)
        self.overlap_tokens = config.get("overlap_tokens", 50)

    def chunk_text(self, text: str, source: str) -> List[Dict[str, Any]]:
        if not text:
            return []
        # Simple fixed-size chunking by character count (coarse token approximation)
        chunk_size = self.max_tokens
        overlap = self.overlap_tokens
        chunks = []
        start = 0
        chunk_idx = 0
        while start < len(text):
            end = start + chunk_size
            chunk_text = text[start:end]
            # Use md5 hash of source + offset as chunk_id to avoid ChromaDB special char issues
            raw_id = f"{source}:{chunk_idx}"
            chunk_id = hashlib.md5(raw_id.encode("utf-8")).hexdigest()
            chunks.append({
                "text": chunk_text,
                "source": source,
                "offset": start,
                "chunk_id": chunk_id,
            })
            start = end - overlap  # overlap
            if start < 0:
                start = 0  # safety
            if end >= len(text):
                break
            chunk_idx += 1
        return chunks
