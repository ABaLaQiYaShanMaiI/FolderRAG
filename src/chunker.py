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
        chunk_id = 0
        while start < len(text):
            end = start + chunk_size
            chunk_text = text[start:end]
            chunks.append({
                "text": chunk_text,
                "source": source,
                "offset": start,
                "chunk_id": f"{source}:{chunk_id}",
            })
            start = end - overlap  # overlap
            if start < 0: start = 0 # safety
            if end >= len(text): break
            chunk_id += 1
        return chunks
