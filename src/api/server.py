from fastapi import FastAPI, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse
from fastapi.middleware.cors import CORSMiddleware
from vector_store import VectorStore
from embedder import Embedder
from .schemas import SearchRequest, SearchResponse, DocResponse
import os

def create_app(vector_store: VectorStore, embedder: Embedder) -> FastAPI:
    app = FastAPI(title="Folder to RAG API")
    
    # CORS
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # Serve static UI
    static_dir = os.path.join(os.path.dirname(__file__), "..", "web", "static")
    app.mount("/static", StaticFiles(directory=static_dir), name="static")

    @app.get("/", response_class=HTMLResponse)
    async def root():
        index_path = os.path.join(static_dir, "index.html")
        if not os.path.exists(index_path):
             return HTMLResponse(content="<h1>Index file not found</h1>")
        with open(index_path, "r", encoding="utf-8") as f:
            return HTMLResponse(content=f.read())

    @app.post("/v1/search", response_model=SearchResponse)
    async def search(request: SearchRequest):
        try:
            results = vector_store.search(request.query, embedder, request.k, request.filters)
            return {"results": results}
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))

    @app.get("/v1/doc/{doc_id}", response_model=DocResponse)
    async def get_doc(doc_id: str):
        doc = vector_store.get_document(doc_id)
        if not doc:
            raise HTTPException(status_code=404, detail="Document not found")
        return doc

    @app.get("/health")
    async def health():
        return {"status": "ok"}

    return app
