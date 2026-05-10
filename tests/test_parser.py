"""
Tests for the parser module.
"""
import os
import tempfile
from src.parser.dispatcher import parse_file


def test_text_parser(sample_text_file):
    result = parse_file(sample_text_file)
    assert result is not None
    assert result["extract_type"] == "text"
    assert result["text"] == "Hello world"


def test_pdf_parser(sample_pdf_file):
    result = parse_file(sample_pdf_file)
    assert result is not None
    assert result["extract_type"] == "text"
    # Content may be empty if pdfminer can't extract from a minimal PDF
    # (no embedded font), so just check the structure is valid


def test_nonexistent_file():
    # Use a path that is guaranteed not to exist on any platform
    nonexistent = os.path.join(tempfile.gettempdir(), "folderrag_nonexistent_file.txt")
    result = parse_file(nonexistent)
    assert result is None
