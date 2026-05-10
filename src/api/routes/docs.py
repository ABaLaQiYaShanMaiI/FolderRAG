from fastapi import APIRouter, HTTPException
from ..schemas import DocResponse
from vector_store import VectorStore


def create_docs_router(vector_store: VectorStore) -> APIRouter:
    router = APIRouter()

    @router.get("/v1/doc/{doc_id}", response_model=DocResponse)
    async def get_doc(doc_id: str):
        doc = vector_store.get_document(doc_id)
        if not doc:
            raise HTTPException(status_code=404, detail="Document not found")
        return doc

    return router
