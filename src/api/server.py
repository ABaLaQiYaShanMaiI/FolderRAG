from fastapi import FastAPI, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse
from fastapi.middleware.cors import CORSMiddleware
from vector_store import VectorStore
from embedder import Embedder
from .routes.search import create_search_router
from .routes.docs import create_docs_router
from pathlib import Path
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

    # Pre-load index.html at startup to avoid sync IO in async handler
    index_path = os.path.join(static_dir, "index.html")
    if os.path.exists(index_path):
        with open(index_path, "r", encoding="utf-8") as f:
            index_html = f.read()
    else:
        index_html = "<h1>Index file not found</h1>"

    @app.get("/", response_class=HTMLResponse)
    async def root():
        return HTMLResponse(content=index_html)

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
