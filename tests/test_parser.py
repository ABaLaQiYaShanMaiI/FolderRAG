import os
import sys
import tempfile
import pytest

# Ensure we can import from src
sys.path.append(os.path.join(os.path.dirname(__file__), "..", "src"))
from parser import parse_file

def test_text_parser():
    with tempfile.NamedTemporaryFile("w", suffix=".txt", delete=False) as f:
        f.write("Hello world")
        fname = f.name
    try:
        config = {"binary": {"hex_preview_bytes": 100}}
        result = parse_file(fname, config)
        assert result["extract_type"] == "text"
        assert result["text"] == "Hello world"
    finally:
        os.unlink(fname)

def test_binary_handler():
    with tempfile.NamedTemporaryFile("wb", suffix=".bin", delete=False) as f:
        f.write(b'\x00\x01\x02\x03Hello\x00World')
        fname = f.name
    try:
        config = {"binary": {"hex_preview_bytes": 100}}
        result = parse_file(fname, config)
        assert result["extract_type"] == "binary"
        # ASCII segments "Hello" and "World" should be extracted if length >=4
        assert "Hello" in result["text"] or "World" in result["text"]
    finally:
        os.unlink(fname)
