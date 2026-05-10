import chromadb
from chromadb.config import Settings
from typing import List, Dict, Any, Optional
from embedder import Embedder
from chunker import Chunker
import logging

logger = logging.getLogger(__name__)


class VectorStore:
    def __init__(self, config: dict):
        persist_dir = config.get("persist_directory", "./data/chroma_db")
        self.client = chromadb.PersistentClient(
            path=persist_dir,
            settings=Settings(anonymized_telemetry=False),
        )
        self.collection = self.client.get_or_create_collection("documents")

    def count(self) -> int:
        """Return the total number of documents in the collection."""
        return self.collection.count()

    def get_file_hash(self, source: str) -> Optional[str]:
        """Retrieve the stored file_hash for a given source, if any."""
        results = self.collection.get(
            where={"source": source},
            limit=1,
            include=["metadatas"],
        )
        if results and results["metadatas"]:
            return results["metadatas"][0].get("file_hash")
        return None

    def upsert_file(self, source, file_hash, modified_at, parsed_data, chunker: Chunker, embedder: Embedder):
        # Delete old chunks from this source first
        self.collection.delete(where={"source": source})

        text = parsed_data.get("text", "")
        chunks = chunker.chunk_text(text, source)
        if not chunks:
            return

        texts = [chunk["text"] for chunk in chunks]
        ids = [chunk["chunk_id"] for chunk in chunks]
        metadatas = []
        for chunk in chunks:
            meta = {
                "source": source,
                "offset": chunk["offset"],
                "chunk_id": chunk["chunk_id"],
                "file_hash": file_hash,
                "modified_at": modified_at,
                "extract_type": parsed_data.get("extract_type", "unknown"),
                "mime": parsed_data.get("metadata", {}).get("mime", ""),
                "hex_preview": parsed_data.get("hex_preview"),
            }
            metadatas.append(meta)

        embeddings = embedder.embed(texts)
        self.collection.add(
            ids=ids,
            embeddings=embeddings,
            metadatas=metadatas,
            documents=texts,
        )
        logger.info(f"Upserted {len(chunks)} chunks for {source}")

    def search(self, query: str, embedder: Embedder, k: int = 5, filters: Dict = None) -> List[Dict]:
        query_embeddings = embedder.embed([query])
        if not query_embeddings:
            return []
        query_embed = query_embeddings[0]
        kwargs = {}
        if filters:
            kwargs["where"] = filters
        results = self.collection.query(
            query_embeddings=[query_embed],
            n_results=k,
            **kwargs,
            include=["metadatas", "documents", "distances"],
        )
        # Format output
        output = []
        if results["ids"] and results["ids"][0]:
            for i in range(len(results["ids"][0])):
                output.append({
                    "id": results["ids"][0][i],
                    "text": results["documents"][0][i],
                    "source": results["metadatas"][0][i].get("source", ""),
                    "offset": results["metadatas"][0][i].get("offset", 0),
                    "score": 1 - results["distances"][0][i],  # lower distance = higher similarity
                    "mime": results["metadatas"][0][i].get("mime", ""),
                    "extract_type": results["metadatas"][0][i].get("extract_type", ""),
                    "hex_preview": results["metadatas"][0][i].get("hex_preview"),
                })
        return output

    def get_document(self, doc_id: str) -> Dict:
        result = self.collection.get(ids=[doc_id], include=["metadatas", "documents"])
        if result and result["ids"]:
            meta = result["metadatas"][0]
            return {
                "id": doc_id,
                "text": result["documents"][0],
                "source": meta.get("source"),
                "offset": meta.get("offset"),
                "mime": meta.get("mime"),
                "extract_type": meta.get("extract_type"),
            }
        return None
