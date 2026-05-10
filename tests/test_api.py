import os
import sys
from fastapi.testclient import TestClient
import pytest

# Ensure we can import from src
sys.path.append(os.path.join(os.path.dirname(__file__), "..", "src"))
from api.server import create_app
from vector_store import VectorStore
from embedder import Embedder

@pytest.fixture
def client():
    # Mock config for tests
    config = {
        "vector_store": {"persist_directory": "./tmp_test_db"},
        "embedder": {"backend": "local", "model_name": "BAAI/bge-small-zh-v1.5"}
    }
    vs = VectorStore(config["vector_store"])
    # We might need to mock or use a very small embedder for tests to run fast
    # For now, let's assume local embedder is okay if environment is setup
    emb = Embedder(config["embedder"])
    app = create_app(vs, emb)
    with TestClient(app) as c:
        yield c
    # Cleanup
    import shutil
    shutil.rmtree("./tmp_test_db", ignore_errors=True)

def test_health(client):
    resp = client.get("/health")
    assert resp.status_code == 200
    assert resp.json() == {"status": "ok"}

def test_search_empty(client):
    resp = client.post("/v1/search", json={"query": "test", "k": 3})
    assert resp.status_code == 200
    assert resp.json() == {"results": []}
