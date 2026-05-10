"""
Shared pytest fixtures for FolderRAG tests.
"""
import os
import tempfile

import pytest


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
def sample_pdf_file():
    """Return path to a real PDF for testing."""
    # Use a real file from the project if available, otherwise skip
    pdf_path = os.path.join(os.path.dirname(__file__), "..", "LICENSE")
    if os.path.exists(pdf_path):
        yield pdf_path
    else:
        pytest.skip("No PDF file available for testing")
