"""
Tests for the FastAPI server.
"""
from fastapi.testclient import TestClient

from src.api.server import create_app
from src.vector_store import VectorStore


def test_health(temp_db_dir, mock_config, fake_embedder):
    config = mock_config
    config["vector_store"]["persist_directory"] = temp_db_dir
    vs = VectorStore(config["vector_store"])
    app = create_app(vs, fake_embedder)
    with TestClient(app) as client:
        resp = client.get("/health")
        assert resp.status_code == 200
        assert resp.json() == {"status": "ok"}


def test_search_empty(temp_db_dir, mock_config, fake_embedder):
    config = mock_config
    config["vector_store"]["persist_directory"] = temp_db_dir
    vs = VectorStore(config["vector_store"])
    app = create_app(vs, fake_embedder)
    with TestClient(app) as client:
        resp = client.post("/v1/search", json={"query": "test", "k": 3})
        assert resp.status_code == 200
        assert resp.json() == {"results": []}


def test_stats(temp_db_dir, mock_config, fake_embedder):
    config = mock_config
    config["vector_store"]["persist_directory"] = temp_db_dir
    vs = VectorStore(config["vector_store"])
    app = create_app(vs, fake_embedder)
    with TestClient(app) as client:
        resp = client.get("/v1/stats")
        assert resp.status_code == 200
        data = resp.json()
        assert "doc_count" in data
        assert data["doc_count"] >= 0
