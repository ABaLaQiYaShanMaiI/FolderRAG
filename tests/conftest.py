"""
Shared pytest fixtures for FolderRAG tests.
"""
import os
import shutil
import tempfile
from pathlib import Path

import pytest


@pytest.fixture(scope="function")
def temp_db_dir():
    """Provide a temporary directory for ChromaDB persistence."""
    tmpdir = tempfile.mkdtemp(prefix="foldrag_test_")
    yield tmpdir
    shutil.rmtree(tmpdir, ignore_errors=True)


@pytest.fixture(scope="function")
def sample_text_file():
    """Create a temporary text file for parser tests."""
    with tempfile.NamedTemporaryFile("w", suffix=".txt", delete=False) as f:
        f.write("Hello world")
        fname = f.name
    yield fname
    if os.path.exists(fname):
        os.unlink(fname)


@pytest.fixture(scope="function")
def sample_binary_file():
    """Create a temporary binary file for parser tests."""
    with tempfile.NamedTemporaryFile("wb", suffix=".bin", delete=False) as f:
        f.write(b'\x00\x01\x02\x03Hello\x00World')
        fname = f.name
    yield fname
    if os.path.exists(fname):
        os.unlink(fname)


@pytest.fixture(scope="function")
def mock_config():
    """Provide a minimal configuration dict for tests."""
    return {
        "vector_store": {"persist_directory": "./tmp_test_db"},
        "embedder": {
            "backend": "local",
            "model_name": "BAAI/bge-small-zh-v1.5"
        },
        "chunk": {
            "max_tokens": 500,
            "overlap_tokens": 50
        },
        "binary": {
            "hex_preview_bytes": 100
        }
    }


class FakeEmbedder:
    """A lightweight stub that replaces the real Embedder in tests.
    Returns zero vectors of dimension 384 (matching bge-small-zh-v1.5)."""
    def __init__(self, config=None):
        pass

    def embed(self, texts):
        return [[0.0] * 384 for _ in texts]


@pytest.fixture(scope="function")
def fake_embedder():
    """Fixture that returns a FakeEmbedder instance instead of the real model."""
    return FakeEmbedder()
