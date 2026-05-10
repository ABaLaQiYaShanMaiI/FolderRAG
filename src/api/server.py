from fastapi import FastAPI, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse
from fastapi.middleware.cors import CORSMiddleware
from src.vector_store import VectorStore
from src.embedder import Embedder
from .routes.search import create_search_router
from .routes.docs import create_docs_router
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

    # Include routers
    app.include_router(create_search_router(vector_store, embedder))
    app.include_router(create_docs_router(vector_store))

    @app.get("/v1/stats")
    async def stats():
        count = vector_store.count()
        return {
            "doc_count": count,
            "last_updated": "实时监控中...",
        }

    @app.get("/health")
    async def health():
        return {"status": "ok"}

    return app
