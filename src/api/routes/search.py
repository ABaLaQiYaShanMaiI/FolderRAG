from fastapi import APIRouter, HTTPException
from ..schemas import SearchRequest, SearchResponse
from src.vector_store import VectorStore
from src.embedder import Embedder

router = APIRouter()


def create_search_router(vector_store: VectorStore, embedder: Embedder) -> APIRouter:
    @router.post("/v1/search", response_model=SearchResponse)
    async def search(request: SearchRequest):
        try:
            results = vector_store.search(request.query, embedder, request.k, request.filters)
            return {"results": results}
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))

    return router
